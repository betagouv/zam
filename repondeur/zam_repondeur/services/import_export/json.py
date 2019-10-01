from collections import Counter

import ujson as json
from pyramid.request import Request

from zam_repondeur.models import Amendement, Lecture

EXCLUDED_FIELDS = {"first_identique_num"}


def export_json(lecture: Lecture, filename: str, request: Request) -> Counter:
    counter = Counter({"amendements": 0, "articles": 0})
    with open(filename, "w", encoding="utf-8-sig") as file_:
        amendements = []
        for amendement in sorted(lecture.amendements):
            amendements.append(export_amendement_for_json(amendement))
            counter["amendements"] += 1
        articles = []
        for article in sorted(lecture.articles):
            articles.append(article.asdict())
            counter["articles"] += 1
        file_.write(
            json.dumps({"amendements": amendements, "articles": articles}, indent=4)
        )
    return counter


def export_amendement_for_json(amendement: Amendement) -> dict:
    return {k: v for k, v in amendement.asdict().items() if k not in EXCLUDED_FIELDS}
