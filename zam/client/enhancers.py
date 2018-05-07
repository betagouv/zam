import re

import CommonMark
from logbook import warn

from loaders import load_docx, load_pdf

PAGINATION_PATTERN = re.compile(r"""
ART\.\s\d+              # Article like `ART. 5` but also `ART. 13 BIS`
(\sBIS(\sB)?|\sTER)?\s  # Article extension (optional) like `BIS B` or `TER`
N°\s\d+(\s\(Rect\))?\s+ # Amendement like `N° 222` but also `N° 18 (Rect)`
\d/\d                   # Pagination like `2/3`
""", re.VERBOSE)


def enhance_amendement(amendement, article, input_dir):
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


def enhance_articles(articles, input_dir, limit):
    for index, article in enumerate(articles):
        if limit and index > limit:
            warn(f'Only {limit} articles enhanced.')
            break
        article['content'] = 'TODO'
        jaune_filename = article['feuilletJaune'].replace('.pdf', '.docx')
        jaune_path = input_dir / 'Jeu de docs - PDF, word'
        jaune_content = load_docx(jaune_path / jaune_filename)
        # Convert jaune to CommonMark to preserve some styles.
        article['jaune'] = CommonMark.commonmark(jaune_content)
        for amendement in article.get('amendements', []):
            enhance_amendement(amendement, article, input_dir)
    return articles
