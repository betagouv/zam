import re
from pathlib import Path

import CommonMark
from logbook import warn

from loaders import load_docx, load_pdf

PAGINATION_PATTERN = re.compile(r"""
ART\.\s\d+              # Article like `ART. 5` but also `ART. 13 BIS`
(\sBIS(\sB)?|\sTER)?\s  # Article extension (optional) like `BIS B` or `TER`
N°\s\d+(\s\(Rect\))?\s+ # Amendement like `N° 222` but also `N° 18 (Rect)`
\d/\d                   # Pagination like `2/3`
""", re.VERBOSE)


def enhance_amendement(
        amendement: dict, article: dict, input_dir: Path) -> None:
    amendement_filename = amendement['document']
    amendement_path = input_dir / 'Jeu de docs - PDF, word'
    content = load_pdf(amendement_path / amendement_filename)
    content = PAGINATION_PATTERN.sub('', content)
    if article['etat'] or article['multiplicatif']:
        prefix = article['titre'].upper()
    else:
        prefix = f'ARTICLE {article["idArticle"]}'
    if content.startswith(prefix):
        content = content[len(prefix) + 1:]
    expose_sommaire = 'EXPOSÉ SOMMAIRE'
    if expose_sommaire in content:
        modification, expose = content.split(expose_sommaire)
        amendement['content'] = modification
        amendement['expose'] = expose
    else:
        amendement['content'] = content


def enhance_articles(articles: list, input_dir: Path, limit: int) -> list:
    for index, article in enumerate(articles):
        if limit and index > limit:
            warn(f'Only {limit} articles enhanced.')
            break
        article['content'] = 'TODO'
        article['pk'] = article['feuilletJaune'].replace('.pdf', '')
        jaune_path = input_dir / 'Jeu de docs - PDF, word'
        jaune_content = load_docx(jaune_path / f'{article["pk"]}.docx')
        # Convert jaune to CommonMark to preserve some styles.
        article['jaune'] = CommonMark.commonmark(jaune_content)
        for amendement in article.get('amendements', []):
            enhance_amendement(amendement, article, input_dir)
    return articles


def strip_styles(content: str) -> str:
    needle = ' style="text-align:justify;"'
    if needle in content:
        return content.replace(needle, '')
    return content


def regroup_reponses(articles: list) -> dict:
    reponses = {}
    for article in articles:
        for amendement in article.get('amendements', []):
            if 'reponse' in amendement:
                reponse = amendement['reponse']
                reponse['presentation'] = strip_styles(reponse['presentation'])
                if 'reponse' in reponse:
                    reponse['reponse'] = strip_styles(reponse['reponse'])
                pk = hash(reponse['presentation'])
                reponses[pk] = reponse
                amendement['reponse']['pk'] = pk
    return reponses
