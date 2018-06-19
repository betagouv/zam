import base64
from collections import OrderedDict
from pathlib import Path
from typing import Any, List, Optional, Tuple

import CommonMark
from dataclasses import dataclass, field
from logbook import warn

from .loaders import load_docx
from .utils import strip_styles


@dataclass
class Article:
    pk: str
    id: int
    titre: str
    etat: Optional[str] = ""
    multiplicatif: Optional[str] = ""
    jaune: Optional[str] = ""
    alineas: Optional[dict] = None
    amendements: Any = field(default_factory=lambda: [])  # List[Amendement]
    document: Optional[str] = ""

    def __str__(self) -> str:
        if self.etat:
            return f"{self.id} {self.etat} {self.multiplicatif}".strip()
        return f"{self.id} {self.multiplicatif}".strip()

    @property
    def slug(self) -> str:
        return f'article-{str(self).replace(" ", "-")}'

    @staticmethod
    def pk_from_raw(raw: dict) -> str:
        return raw["document"][: -len(".pdf")]


class Articles(OrderedDict):
    @classmethod
    def load(cls, items: List[dict]) -> "Articles":
        articles = cls()
        for raw_article in items:
            article = Article(**raw_article)  # type: ignore # dataclasses
            article.amendements = []  # Reset, loaded after.
            articles[article.pk] = article
        return articles

    def load_jaunes(self, items: List[dict], jaunes_folder: Path) -> None:
        jaunes_path = Path(jaunes_folder)
        for raw_article in items:
            try:
                article = self.get_from_raw(raw_article)
            except KeyError:
                continue
            jaune_name = raw_article["feuilletJaune"].replace(".pdf", ".docx")
            jaune_content = load_docx(jaunes_path / jaune_name)
            # Convert jaune to CommonMark to preserve some styles.
            article.jaune = CommonMark.commonmark(jaune_content)

    def load_contents(self, items: List[dict]) -> None:
        for article_content in items:
            article_num = article_content["titre"].replace(" ", "-").replace("1er", "1")
            pk = f'article-{article_num}'
            if pk in self:
                self[pk].alineas = article_content["alineas"]
                if "section" in article_content:
                    self[pk].titre = [
                        item["titre"]
                        for item in items
                        if article_content["section"] == item.get("id")
                    ][0]

    def get_from_raw(self, raw: dict) -> Article:
        return self[Article.pk_from_raw(raw)]


@dataclass
class Amendement:
    pk: str
    id: int
    groupe: dict
    article: Article
    gouvernemental: bool = False
    auteur: Optional[str] = ""
    objet: Optional[str] = ""
    dispositif: Optional[str] = ""
    resume: Optional[str] = ""
    document: Optional[str] = ""
    etat: Optional[str] = ""

    def __str__(self) -> str:
        return self.pk

    @staticmethod
    def pk_from_raw(raw: dict) -> str:
        return raw["document"][: -len("-00.pdf")]


class Amendements(OrderedDict):
    @classmethod
    def load(cls, items: List[dict], articles: Articles) -> "Amendements":
        amendements = cls()
        for raw_article in items:
            article = articles[raw_article["pk"]]
            for raw_amendement in raw_article.get("amendements", []):
                raw_amendement["article"] = article
                amendement = Amendement(**raw_amendement)  # type: ignore # dataclasses
                amendements[amendement.pk] = amendement
                article.amendements.append(amendement)
        return amendements

    def get_from_raw(self, raw: dict) -> Amendement:
        return self[Amendement.pk_from_raw(raw)]


@dataclass
class Reponse:
    pk: str
    avis: str
    presentation: str
    content: str
    amendements: List[Amendement]
    article: Article

    def __str__(self) -> str:
        return self.pk

    @staticmethod
    def pk_from_raw(raw: dict) -> str:
        unique = raw.get("presentation", str(raw["idReponse"]))
        return base64.b64encode(unique.encode()).decode()

    @property
    def favorable(self):
        return self.avis.startswith("Favorable")

    @property
    def sagesse(self):
        return self.avis == "Sagesse"


class Reponses(OrderedDict):
    @classmethod
    def load(
        cls, items: List[dict], articles: Articles, amendements: Amendements
    ) -> "Reponses":
        reponses = cls()
        for raw_article in items:
            try:
                article = articles.get_from_raw(raw_article)
            except KeyError:
                continue
            for raw_amendement in raw_article.get("amendements", []):
                if "reponse" not in raw_amendement:
                    continue
                raw_reponse = raw_amendement["reponse"]
                pk = Reponse.pk_from_raw(raw_reponse)
                try:
                    amendement = amendements.get_from_raw(raw_amendement)
                except KeyError:
                    warn(
                        f"Amendement {raw_amendement['idAmendement']} not "
                        f"found for Reponse {raw_reponse['idReponse']}."
                    )
                    continue
                if pk in reponses:
                    reponses[pk].amendements.append(amendement)
                    continue
                reponses[pk] = Reponse(  # type: ignore # dataclasses
                    pk=pk,
                    avis=raw_reponse["avis"],
                    presentation=strip_styles(raw_reponse.get("presentation", "")),
                    content=strip_styles(raw_reponse.get("reponse", "")),
                    article=article,
                    amendements=[amendement],
                )
        return reponses


def load_data(
    aspirateur_items: List[dict],
    drupal_items: List[dict] = [],
    articles_contents: List[dict] = [],
    jaunes_folder: Path = Path(),
) -> Tuple[Articles, Amendements, Reponses]:
    articles = Articles.load(aspirateur_items)
    amendements = Amendements.load(aspirateur_items, articles)
    if drupal_items:
        articles.load_jaunes(drupal_items, jaunes_folder)
        reponses = Reponses.load(drupal_items, articles, amendements)
    else:
        reponses = Reponses()
    if articles_contents:
        articles.load_contents(articles_contents)
    return articles, amendements, reponses
