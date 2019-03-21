import logging
from collections import Counter
from datetime import datetime
from typing import BinaryIO, Dict

import ujson as json
from pyramid.httpexceptions import HTTPFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config
from sqlalchemy.orm import joinedload

from zam_repondeur.clean import clean_html
from zam_repondeur.message import Message
from zam_repondeur.models import (
    DBSession,
    Amendement,
    Article,
    Lecture,
    User,
    get_one_or_create,
)
from zam_repondeur.models.events.amendement import (
    AmendementTransfere,
    AvisAmendementModifie,
    ObjetAmendementModifie,
    ReponseAmendementModifiee,
    CommentsAmendementModifie,
)
from zam_repondeur.resources import LectureResource
from zam_repondeur.utils import normalize_avis, normalize_num, normalize_reponse


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
        lecture.modified_at = datetime.utcnow()

    if counter["reponses_errors"] or counter["articles_errors"]:
        message = "Le fichier de sauvegarde n’a pas pu être chargé"
        if counter["reponses_errors"]:
            message += f" pour {counter['reponses_errors']} amendement(s)"
            if counter["articles_errors"]:
                message += f" et {counter['articles_errors']} article(s)"
        elif counter["articles_errors"]:
            message += f"pour {counter['articles_errors']} article(s)"
        request.session.flash(Message(cls="warning", text=message))

    return HTTPFound(location=next_url)


def _import_backup_from_json_file(
    request: Request,
    backup_file: BinaryIO,
    lecture: Lecture,
    amendements: Dict[int, Amendement],
    articles: Dict[int, Article],
) -> Counter:
    previous_reponse = ""
    counter = Counter(
        {"reponses": 0, "articles": 0, "reponses_errors": 0, "articles_errors": 0}
    )
    backup = json.loads(backup_file.read().decode("utf-8-sig"))

    for item in backup.get("amendements", []):
        try:
            numero = item["num"]
            avis = item["avis"] or ""
            objet = item["objet"] or ""
            reponse = item["reponse"] or ""
        except KeyError:
            counter["reponses_errors"] += 1
            continue

        try:
            num = normalize_num(numero)
        except ValueError:
            logging.warning("Invalid amendement number %r", numero)
            counter["reponses_errors"] += 1
            continue

        amendement = amendements.get(num)
        if not amendement:
            logging.warning("Could not find amendement number %r", num)
            counter["reponses_errors"] += 1
            continue

        avis = normalize_avis(avis)
        if avis != (amendement.user_content.avis or ""):
            AvisAmendementModifie.create(request, amendement, avis)

        objet = clean_html(objet)
        if objet != (amendement.user_content.objet or ""):
            ObjetAmendementModifie.create(request, amendement, objet)

        reponse = clean_html(normalize_reponse(reponse, previous_reponse))
        if reponse != (amendement.user_content.reponse or ""):
            ReponseAmendementModifiee.create(request, amendement, reponse)

        if "comments" in item:
            comments = clean_html(item["comments"])
            if comments != (amendement.user_content.comments or ""):
                CommentsAmendementModifie.create(request, amendement, comments)

        if "affectation_email" in item and item["affectation_email"]:
            email = item["affectation_email"]
            user, created = get_one_or_create(User, email=User.normalize_email(email))
            if created:
                if item.get("affectation_name"):
                    user.name = item["affectation_name"]
                if lecture.owned_by_team:
                    user.teams.append(lecture.owned_by_team)
            target_table = user.table_for(lecture)
            DBSession.add(target_table)

            old = str(amendement.user_table.user) if amendement.user_table else ""
            new = str(target_table.user) if target_table else ""
            if amendement.user_table is target_table:
                continue
            amendement.user_table = target_table
            AmendementTransfere.create(request, amendement, old, new)

        previous_reponse = reponse
        counter["reponses"] += 1

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
        elif "titre" in item:  # To handle old backups.
            article.user_content.title = item["titre"]
        if "presentation" in item:
            article.user_content.presentation = item["presentation"]
        counter["articles"] += 1

    return counter
