import logging
from collections import Counter
from typing import BinaryIO, Dict

import ujson as json
from pyramid.request import Request

from zam_repondeur.models import Amendement, Article, Lecture, Team
from zam_repondeur.services.import_export.common import import_amendement


def _import_backup_from_json_file(
    request: Request,
    backup_file: BinaryIO,
    lecture: Lecture,
    amendements: Dict[int, Amendement],
    articles: Dict[str, Article],
    team: Team,
) -> Counter:
    previous_reponse = ""
    counter = Counter(
        {"reponses": 0, "articles": 0, "reponses_errors": 0, "articles_errors": 0}
    )
    backup = json.loads(backup_file.read().decode("utf-8-sig"))

    for item in backup.get("amendements", []):
        import_amendement(
            request, lecture, amendements, item, counter, previous_reponse, team
        )

    for item in backup.get("articles", []):
        try:
            sort_key_as_str = item["sort_key_as_str"]
        except KeyError:
            counter["articles_errors"] += 1
            continue

        article = articles.get(sort_key_as_str)
        if not article:
            logging.warning("Could not find article %r", item)
            counter["articles_errors"] += 1
            continue

        if "title" in item:
            article.user_content.title = item["title"]
        if "presentation" in item:
            article.user_content.presentation = item["presentation"]
        counter["articles"] += 1

    return counter


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
