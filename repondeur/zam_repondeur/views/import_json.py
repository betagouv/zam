import logging
from collections import Counter
from typing import BinaryIO, Dict

import ujson as json
from pyramid.httpexceptions import HTTPFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config
from sqlalchemy.orm import joinedload

from zam_repondeur.message import Message
from zam_repondeur.models import Amendement, Article, Lecture, Team
from zam_repondeur.models.events.lecture import ReponsesImporteesJSON
from zam_repondeur.resources import LectureResource

from .import_items import import_amendement


@view_config(context=LectureResource, name="import_backup", request_method="POST")
def import_backup(context: LectureResource, request: Request) -> Response:

    lecture = context.model(joinedload("articles"))

    next_url = request.resource_url(context["amendements"])

    # We cannot just do `if not POST["backup"]`, as FieldStorage does not want
    # to be cast to a boolean.
    if request.POST["backup"] == b"":
        request.session.flash(
            Message(cls="warning", text="Veuillez d’abord sélectionner un fichier")
        )
        return HTTPFound(location=request.resource_url(context, "options"))

    try:
        counter = _import_backup_from_json_file(
            request=request,
            backup_file=request.POST["backup"].file,
            lecture=lecture,
            amendements={
                amendement.num: amendement for amendement in lecture.amendements
            },
            articles={article.sort_key_as_str: article for article in lecture.articles},
            team=context.dossier_resource.dossier.team,
        )
    except ValueError as exc:
        request.session.flash(Message(cls="danger", text=str(exc)))
        return HTTPFound(location=next_url)

    if counter["reponses"] or counter["articles"]:
        if counter["reponses"]:
            message = f"{counter['reponses']} réponse(s) chargée(s) avec succès"
            if counter["articles"]:
                message += f", {counter['articles']} article(s) chargé(s) avec succès"
        elif counter["articles"]:
            message = f"{counter['articles']} article(s) chargé(s) avec succès"
        request.session.flash(Message(cls="success", text=message))
        ReponsesImporteesJSON.create(request, lecture)

    if counter["reponses_errors"] or counter["articles_errors"]:
        message = "Le fichier de sauvegarde n’a pas pu être chargé"
        if counter["reponses_errors"]:
            message += f" pour {counter['reponses_errors']} amendement(s)"
            if counter["articles_errors"]:
                message += f" et {counter['articles_errors']} article(s)"
        elif counter["articles_errors"]:
            message += f" pour {counter['articles_errors']} article(s)"
        request.session.flash(Message(cls="warning", text=message))

    return HTTPFound(location=next_url)


def _import_backup_from_json_file(
    request: Request,
    backup_file: BinaryIO,
    lecture: Lecture,
    amendements: Dict[int, Amendement],
    articles: Dict[int, Article],
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
