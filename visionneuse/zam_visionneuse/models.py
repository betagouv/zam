import base64
import os
from collections import OrderedDict

import CommonMark
from dataclasses import dataclass, field
from logbook import warn
from pathlib import Path
from typing import Any, List, Tuple

from .decorators import require_env_vars
from .loaders import load_docx
from .utils import strip_styles


@dataclass
class Article:
    pk: str
    id: int
    title: str
    state: str = ""
    multiplier: str = ""
    jaune: str = ""
    content: str = "TODO"
    amendements: Any = field(default_factory=lambda: [])  # List[Amendement]

    def __str__(self) -> str:
        if self.state:
            return f"{self.id} {self.state} {self.multiplier}".strip()
        return f"{self.id} {self.multiplier}".strip()

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
            pk = Article.pk_from_raw(raw_article)
            articles[pk] = Article(  # type: ignore # dataclasses
                pk=pk,
                id=raw_article["idArticle"],
                title=raw_article["titre"],
                state=raw_article["etat"],
                multiplier=raw_article["multiplicatif"],
            )
        return articles

    def load_jaunes(self, items: List[dict]) -> None:
        jaunes_path = Path(os.environ["ZAM_JAUNES_SOURCE"])
        for raw_article in items:
            try:
                article = self.get_from_raw(raw_article)
            except KeyError:
                continue
            jaune_name = raw_article["feuilletJaune"].replace(".pdf", ".docx")
            jaune_content = load_docx(jaunes_path / jaune_name)
            # Convert jaune to CommonMark to preserve some styles.
            article.jaune = CommonMark.commonmark(jaune_content)

    def get_from_raw(self, raw: dict) -> Article:
        return self[Article.pk_from_raw(raw)]


@dataclass
class Amendement:
    pk: str
    id: int
    article: Article
    group: dict
    authors: str = ""
    is_gouvernemental: bool = False
    summary: str = ""
    content: str = ""
    document: str = ""

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
            article = articles.get_from_raw(raw_article)
            for raw_amendement in raw_article.get("amendements", []):
                pk = Amendement.pk_from_raw(raw_amendement)
                id_ = raw_amendement["idAmendement"]
                auteurs = raw_amendement.get("auteurs")
                if auteurs:
                    authors = ", ".join(
                        author["auteur"].strip() for author in auteurs
                    )
                group = None
                if "groupesParlementaires" in raw_amendement:
                    group = raw_amendement["groupesParlementaires"][0]
                    group = {
                        "label": group["libelle"],
                        "color": group["couleur"],
                    }
                amendement = Amendement(  # type: ignore # dataclasses
                    pk=pk,
                    id=id_,
                    authors=authors,
                    group=group,
                    article=article,
                    document=raw_amendement["document"],
                    is_gouvernemental=raw_amendement["gouvernemental"],
                    summary=raw_amendement["objet"],
                    content=raw_amendement["dispositif"],
                )
                amendements[pk] = amendement
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
                    presentation=strip_styles(
                        raw_reponse.get("presentation", "")
                    ),
                    content=strip_styles(raw_reponse.get("reponse", "")),
                    article=article,
                    amendements=[amendement],
                )
        return reponses


@require_env_vars(env_vars=["ZAM_JAUNES_SOURCE"])
def load_data(
    drupal_items: List[dict], aspirateur_items: List[dict]
) -> Tuple[Articles, Amendements, Reponses]:
    articles = Articles.load(aspirateur_items)
    articles.load_jaunes(drupal_items)
    amendements = Amendements.load(aspirateur_items, articles)
    reponses = Reponses.load(drupal_items, articles, amendements)
    return articles, amendements, reponses
