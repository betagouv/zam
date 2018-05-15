import json
from io import BytesIO
from pathlib import Path
import re
from typing import Dict, Tuple

import CommonMark
from logbook import warn
import pdfminer.high_level

from decorators import check_existence
from models import Amendement, Article, Reponse
from parsers import parse_docx
from utils import positive_hash, strip_styles

PAGINATION_PATTERN = re.compile(r"""
ART\.\s\d+              # Article like `ART. 5` but also `ART. 13 BIS`
(\sBIS(\sB)?|\sTER)?\s  # Article extension (optional) like `BIS B` or `TER`
N°\s\d+(\s\(Rect\))?\s+ # Amendement like `N° 222` but also `N° 18 (Rect)`
\d/\d                   # Pagination like `2/3`
""", re.VERBOSE)


def load_article(article: dict, input_dir: Path) -> Article:
    pk = article['document'][:-len('.pdf')]
    id_ = article['idArticle']
    title = article['titre']
    state = article['etat']
    multiplier = article['multiplicatif']
    jaune_path = input_dir / 'Jeu de docs - PDF, word'
    jaune_file_path = article['feuilletJaune'].replace('.pdf', '.docx')
    jaune_content = load_docx(jaune_path / jaune_file_path)
    # Convert jaune to CommonMark to preserve some styles.
    jaune = CommonMark.commonmark(jaune_content)
    return Article(pk=pk, id=id_, title=title, content='TODO', state=state,
                   multiplier=multiplier, jaune=jaune, amendements=[])


def load_amendement(
        amendement: dict, article: Article, input_dir: Path) -> Amendement:
    pk = amendement['document'][:-len('.pdf')]
    id_ = amendement['idAmendement']
    authors = ', '.join(author['auteur'] for author in amendement['auteurs'])
    group = None
    if 'groupesParlementaires' in amendement:
        group = amendement['groupesParlementaires'][0]
        group = {
            'label': group['libelle'],
            'color': group['couleur']
        }
    amendement_filename = amendement['document']
    amendement_path = input_dir / 'Jeu de docs - PDF, word'
    content = load_pdf(amendement_path / amendement_filename)
    content = PAGINATION_PATTERN.sub('', content)
    if article.state or article.multiplier:
        prefix = article.title.upper()
    else:
        prefix = f'ARTICLE {article.id}'
    if content.startswith(prefix):
        content = content[len(prefix) + 1:]
    expose_sommaire = 'EXPOSÉ SOMMAIRE'
    summary = None
    if expose_sommaire in content:
        content, summary = content.split(expose_sommaire)
    return Amendement(pk=pk, id=id_, authors=authors, group=group,
                      article=article, content=content, summary=summary)


def load_reponse(
        pk: str, reponse: dict, amendement: Amendement,
        article: Article) -> Reponse:
    presentation = strip_styles(reponse['presentation'])
    content = None
    if 'reponse' in reponse:
        content = strip_styles(reponse['reponse'])
    avis = reponse['avis']
    return Reponse(
        pk=pk,
        avis=avis,
        presentation=presentation,
        content=content,
        article=article,
        amendements=[amendement])


def load_reponses(items: list, input_dir: Path, limit: int
                  ) -> Tuple[Dict[str, Reponse], Dict[str, Article]]:
    reponses: dict = {}
    articles: dict = {}
    for index, article in enumerate(items):
        if limit and index > limit:
            warn(f'Only {limit} items loaded.')
            break
        amendements = article.get('amendements', [])
        article = load_article(article, input_dir)
        for amendement in amendements:
            if 'reponse' in amendement:
                reponse = amendement['reponse']
                amendement = load_amendement(amendement, article, input_dir)
                reponse_pk = positive_hash(reponse['presentation'])
                if reponse_pk in reponses:
                    reponses[reponse_pk] += amendement
                else:
                    reponses[reponse_pk] = load_reponse(
                        reponse_pk, reponse, amendement, article)
                article += amendement
        if article.amendements:
            articles[article.pk] = article
    return reponses, articles


def load_json(source_path: Path) -> dict:
    with open(source_path) as source:
        return json.loads(source.read())


@check_existence
def load_pdf(source_path: Path) -> str:
    target = BytesIO()
    with open(source_path, 'rb') as source:
        pdfminer.high_level.extract_text_to_fp(source, target, codec='latin-1')
    content = target.getvalue().decode()
    # Skip optional headers.
    separator = '----------'
    if separator in content:
        headers, content = content.split(separator)
    return content.strip()


@check_existence
def load_docx(source_path: Path) -> str:
    with open(source_path, 'rb') as source:
        content = parse_docx(source)
    # Get rid of (not proper docx) headers.
    return '\n'.join(part for part in content.split('\n')[9:])
