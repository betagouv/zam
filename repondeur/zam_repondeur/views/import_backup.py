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

from zam_repondeur.message import Message
from zam_repondeur.models import Amendement, Article
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
        return HTTPFound(location=next_url)

    try:
        counter = _import_backup_from_json_file(
            backup_file=request.POST["backup"].file,
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
    backup_file: BinaryIO,
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
            objet = item["observations"] or ""
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

        amendement.avis = normalize_avis(avis)
        amendement.observations = objet
        reponse = normalize_reponse(reponse, previous_reponse)
        amendement.reponse = reponse
        if "affectation" in item:
            amendement.affectation = item["affectation"]
        if "comments" in item:
            amendement.comments = item["comments"]
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

        if "titre" in item:
            article.titre = item["titre"]
        if "contenu" in item:
            article.contenu = item["contenu"]
        counter["articles"] += 1

    return counter
