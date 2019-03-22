import ujson as json
from pyramid.request import Request

from zam_repondeur.models import Lecture

from .common import export_amendement


def write_json(lecture: Lecture, filename: str, request: Request) -> int:
    nb_rows = 0
    with open(filename, "w", encoding="utf-8-sig") as file_:
        amendements = []
        for amendement in sorted(lecture.amendements):
            amendements.append(export_amendement(amendement, strip_html=False))
            nb_rows += 1
        articles = []
        for article in sorted(lecture.articles):
            articles.append(article.asdict())
            nb_rows += 1
        file_.write(
            json.dumps({"amendements": amendements, "articles": articles}, indent=4)
        )
    return nb_rows
