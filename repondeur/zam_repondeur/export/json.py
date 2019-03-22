from collections import Counter

import ujson as json
from pyramid.request import Request

from zam_repondeur.models import Amendement, Lecture


EXCLUDED_FIELDS = {"first_identique_num"}


def write_json(lecture: Lecture, filename: str, request: Request) -> Counter:
    counter = Counter({"amendements": 0, "articles": 0})
    with open(filename, "w", encoding="utf-8-sig") as file_:
        amendements = []
        for amendement in sorted(lecture.amendements):
            amendement_export = export_amendement_for_json(amendement)
            amendement_export["events"] = {
                str(event.created_at_timestamp): event.asdict()
                for event in amendement.events
            }
            counter["amendements_events"] += len(amendement_export["events"])
            amendements.append(amendement_export)
            counter["amendements"] += 1
        articles = []
        for article in sorted(lecture.articles):
            article_export = article.asdict()
            article_export["events"] = {
                str(event.created_at_timestamp): event.asdict()
                for event in article.events
            }
            counter["articles_events"] += len(article_export["events"])
            articles.append(article_export)
            counter["articles"] += 1
        file_.write(
            json.dumps({"amendements": amendements, "articles": articles}, indent=4)
        )
    return counter


def export_amendement_for_json(amendement: Amendement) -> dict:
    return {k: v for k, v in amendement.asdict().items() if k not in EXCLUDED_FIELDS}
