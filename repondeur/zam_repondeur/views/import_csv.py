import csv
import io
import logging
from collections import Counter
from datetime import datetime
from typing import BinaryIO, Dict, TextIO

from pyramid.httpexceptions import HTTPFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config

from zam_repondeur.clean import clean_html
from zam_repondeur.message import Message
from zam_repondeur.models import DBSession, Amendement, Lecture, User, get_one_or_create
from zam_repondeur.models.events.amendement import (
    AmendementTransfere,
    AvisAmendementModifie,
    ObjetAmendementModifie,
    ReponseAmendementModifiee,
    CommentsAmendementModifie,
)
from zam_repondeur.resources import LectureResource
from zam_repondeur.utils import normalize_avis, normalize_num, normalize_reponse


class CSVError(Exception):
    pass


@view_config(context=LectureResource, name="import_csv", request_method="POST")
def import_csv(context: LectureResource, request: Request) -> Response:

    lecture = context.model()

    next_url = request.resource_url(context["amendements"])

    # We cannot just do `if not POST["reponses"]`, as FieldStorage does not want
    # to be cast to a boolean.
    if request.POST["reponses"] == b"":
        request.session.flash(
            Message(cls="warning", text="Veuillez d’abord sélectionner un fichier")
        )
        return HTTPFound(location=request.resource_url(context, "options"))

    try:
        counter = _import_reponses_from_csv_file(
            request=request,
            reponses_file=request.POST["reponses"].file,
            lecture=lecture,
            amendements={
                amendement.num: amendement for amendement in lecture.amendements
            },
        )
    except CSVError as exc:
        request.session.flash(Message(cls="danger", text=str(exc)))
        return HTTPFound(location=next_url)

    if counter["reponses"]:
        request.session.flash(
            Message(
                cls="success",
                text=f"{counter['reponses']} réponse(s) chargée(s) avec succès",
            )
        )
        lecture.modified_at = datetime.utcnow()

    if counter["reponses_errors"]:
        request.session.flash(
            Message(
                cls="warning",
                text=(
                    f"{counter['reponses_errors']} réponse(s) "
                    "n’ont pas pu être chargée(s). "
                    "Pour rappel, il faut que le fichier CSV contienne au moins "
                    "les noms de colonnes suivants « Num amdt », "
                    "« Avis du Gouvernement », « Objet amdt » et « Réponse »."
                ),
            )
        )

    return HTTPFound(location=next_url)


def _import_reponses_from_csv_file(
    request: Request,
    reponses_file: BinaryIO,
    lecture: Lecture,
    amendements: Dict[int, Amendement],
) -> Counter:
    previous_reponse = ""
    counter = Counter({"reponses": 0, "reponses_errors": 0})

    reponses_text_file = io.TextIOWrapper(reponses_file, encoding="utf-8-sig")

    delimiter = _guess_csv_delimiter(reponses_text_file)

    for line in csv.DictReader(reponses_text_file, delimiter=delimiter):
        try:
            numero = line["Num amdt"]
            avis = line["Avis du Gouvernement"] or ""
            objet = line["Objet amdt"] or ""
            reponse = line["Réponse"] or ""
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

        if "Commentaires" in line:
            comments = clean_html(line["Commentaires"])
            if comments != (amendement.user_content.comments or ""):
                CommentsAmendementModifie.create(request, amendement, comments)

        if "Affectation (email)" in line and line["Affectation (email)"]:
            email = line["Affectation (email)"]
            user, created = get_one_or_create(User, email=User.normalize_email(email))
            if created:
                if line.get("Affectation (nom)"):
                    user.name = line["Affectation (nom)"]
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

    return counter


def _guess_csv_delimiter(text_file: TextIO) -> str:
    try:
        sample = text_file.readline()
    except UnicodeDecodeError:
        raise CSVError("Le fichier n’est pas encodé en UTF-8")
    except Exception:
        raise CSVError("Le format du fichier n’est pas reconnu")

    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
    except csv.Error:
        raise CSVError(
            "Le fichier CSV n’utilise pas un délimiteur reconnu "
            "(virgule, point-virgule ou tabulation)"
        )

    text_file.seek(0)

    return dialect.delimiter
