import base64
import os
import re
from collections import OrderedDict

import CommonMark
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, List, Tuple

from decorators import require_env_vars
from loaders import load_docx, load_pdf
from utils import strip_styles, warnumerate

PAGINATION_PATTERN = re.compile(r"""
ART\.\s\d+              # Article like `ART. 5` but also `ART. 13 BIS`
(\sBIS(\sB)?|\sTER)?\s  # Article extension (optional) like `BIS B` or `TER`
N°\s\d+(\s\(Rect\))?\s+ # Amendement like `N° 222` but also `N° 18 (Rect)`
\d/\d                   # Pagination like `2/3`
""", re.VERBOSE)


@dataclass
class Article:
    pk: str
    id: int
    title: str
    state: str = ''
    multiplier: str = ''
    jaune: str = ''
    content: str = 'TODO'
    amendements: Any = field(default_factory=lambda: [])  # List[Amendement]

    def __str__(self) -> str:
        return f'{self.id} {self.state} {self.multiplier}'

    @staticmethod
    def pk_from_raw(raw: dict) -> str:
        return raw['document'][:-len('.pdf')]


class Articles(OrderedDict):

    @classmethod
    def load(cls, items: list, limit: int):  # -> Articles
        articles = cls()
        for raw_article in warnumerate(items, limit):
            pk = Article.pk_from_raw(raw_article)
            articles[pk] = Article(
                pk=pk,
                id=raw_article['idArticle'],
                title=raw_article['titre'],
                state=raw_article['etat'],
                multiplier=raw_article['multiplicatif']
            )
        return articles

    def load_jaunes(self, items: list, input_dir: Path, limit: int) -> None:
        for raw_article in warnumerate(items, limit):
            article = self.get_from_raw(raw_article)
            jaune_content = load_docx(
                input_dir / 'Jeu de docs - PDF, word' /
                raw_article['feuilletJaune'].replace('.pdf', '.docx'))
            # Convert jaune to CommonMark to preserve some styles.
            article.jaune = CommonMark.commonmark(jaune_content)

    def get_from_raw(self, raw: dict) -> Article:
        return self[Article.pk_from_raw(raw)]


@dataclass
class Amendement:
    pk: str
    id: int
    article: Article
    authors: str
    group: dict
    content: str = ''
    summary: str = ''
    document: str = ''

    def __str__(self) -> str:
        return self.pk

    @staticmethod
    def pk_from_raw(raw: dict) -> str:
        return raw['document'][:-len('.pdf')]


class Amendements(OrderedDict):

    @classmethod
    def load(
        cls, items: dict, articles: Articles, limit: int
    ):  # -> Amendements
        amendements = cls()
        for raw_article in warnumerate(items, limit):
            article = articles.get_from_raw(raw_article)
            for raw_amendement in raw_article.get('amendements', []):
                pk = Amendement.pk_from_raw(raw_amendement)
                id_ = raw_amendement['idAmendement']
                authors = ', '.join(author['auteur']
                                    for author in raw_amendement['auteurs'])
                group = None
                if 'groupesParlementaires' in raw_amendement:
                    group = raw_amendement['groupesParlementaires'][0]
                    group = {
                        'label': group['libelle'],
                        'color': group['couleur']
                    }
                amendement = Amendement(
                    pk=pk,
                    id=id_,
                    authors=authors,
                    group=group,
                    article=article,
                    document=raw_amendement['document']
                )
                amendements[pk] = amendement
                article.amendements.append(amendement)
        return amendements

    def load_contents(self, input_dir: Path) -> None:
        for amendement in self.values():
            amendement_filename = amendement.document
            amendement_path = input_dir / 'Jeu de docs - PDF, word'
            content = load_pdf(amendement_path / amendement.document)
            content = PAGINATION_PATTERN.sub('', content)
            if amendement.article.state or amendement.article.multiplier:
                prefix = amendement.article.title.upper()
            else:
                prefix = f'ARTICLE {amendement.article.id}'
            if content.startswith(prefix):
                amendement.content = content[len(prefix) + 1:]
            expose_sommaire = 'EXPOSÉ SOMMAIRE'
            if expose_sommaire in amendement.content:
                amendement.content, amendement.summary = \
                    amendement.content.split(expose_sommaire)

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
        return base64.b64encode(raw['presentation'].encode()).decode()


class Reponses(OrderedDict):

    @classmethod
    def load(
        cls, items: dict, articles: Articles, amendements: Amendements,
        limit: int
    ):  # -> Reponses
        reponses = cls()
        for raw_article in warnumerate(items, limit):
            article = articles.get_from_raw(raw_article)
            for raw_amendement in raw_article.get('amendements', []):
                if 'reponse' not in raw_amendement:
                    continue
                raw_reponse = raw_amendement['reponse']
                amendement = amendements.get_from_raw(raw_amendement)
                pk = Reponse.pk_from_raw(raw_reponse)
                if pk in reponses:
                    reponses[pk].amendements.append(amendement)
                    continue
                reponses[pk] = Reponse(
                    pk=pk,
                    avis=raw_reponse['avis'],
                    presentation=strip_styles(raw_reponse['presentation']),
                    content=strip_styles(raw_reponse.get('reponse', '')),
                    article=article,
                    amendements=[amendement]
                )
        return reponses


@require_env_vars(env_vars=['ZAM_INPUT'])
def load_data(
    items: dict, limit: int=None
) -> Tuple[Articles, Amendements, Reponses]:
    input_path = Path(os.environ['ZAM_INPUT'])
    articles = Articles.load(items, limit)
    articles.load_jaunes(items, input_path, limit)
    amendements = Amendements.load(items, articles, limit)
    amendements.load_contents(input_path)
    reponses = Reponses.load(items, articles, amendements, limit)
    return articles, amendements, reponses
