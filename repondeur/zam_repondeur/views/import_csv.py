import csv
import io
import logging
from datetime import datetime
from typing import BinaryIO, Dict, TextIO, Tuple

from pyramid.httpexceptions import HTTPFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config

from zam_repondeur.clean import clean_html
from zam_repondeur.message import Message
from zam_repondeur.models import DBSession, Amendement, Lecture, User, get_one_or_create
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
        reponses_count, errors_count = _import_reponses_from_csv_file(
            reponses_file=request.POST["reponses"].file,
            lecture=lecture,
            amendements={
                amendement.num: amendement for amendement in lecture.amendements
            },
        )
    except CSVError as exc:
        request.session.flash(Message(cls="danger", text=str(exc)))
        return HTTPFound(location=next_url)

    if reponses_count:
        request.session.flash(
            Message(
                cls="success",
                text=f"{reponses_count} réponse(s) chargée(s) avec succès",
            )
        )
        lecture.modified_at = datetime.utcnow()

    if errors_count:
        request.session.flash(
            Message(
                cls="warning",
                text=(
                    f"{errors_count} réponse(s) n’ont pas pu être chargée(s). "
                    "Pour rappel, il faut que le fichier CSV contienne au moins "
                    "les noms de colonnes suivants « Num amdt », "
                    "« Avis du Gouvernement », « Objet amdt » et « Réponse »."
                ),
            )
        )

    return HTTPFound(location=next_url)


def _import_reponses_from_csv_file(
    reponses_file: BinaryIO, lecture: Lecture, amendements: Dict[int, Amendement]
) -> Tuple[int, int]:
    previous_reponse = ""
    reponses_count = 0
    errors_count = 0

    reponses_text_file = io.TextIOWrapper(reponses_file, encoding="utf-8-sig")

    delimiter = _guess_csv_delimiter(reponses_text_file)

    for line in csv.DictReader(reponses_text_file, delimiter=delimiter):
        try:
            numero = line["Num amdt"]
            avis = line["Avis du Gouvernement"] or ""
            objet = line["Objet amdt"] or ""
            reponse = line["Réponse"] or ""
        except KeyError:
            errors_count += 1
            continue

        try:
            num = normalize_num(numero)
        except ValueError:
            logging.warning("Invalid amendement number %r", numero)
            errors_count += 1
            continue

        amendement = amendements.get(num)
        if not amendement:
            logging.warning("Could not find amendement number %r", num)
            errors_count += 1
            continue

        amendement.user_content.avis = normalize_avis(avis)
        amendement.user_content.objet = clean_html(objet)
        reponse = normalize_reponse(reponse, previous_reponse)
        amendement.user_content.reponse = clean_html(reponse)
        if "Commentaires" in line:
            amendement.user_content.comments = clean_html(line["Commentaires"])
        if "Affectation (email)" in line and line["Affectation (email)"]:
            email = line["Affectation (email)"]
            user, created = get_one_or_create(User, email=User.normalize_email(email))
            if created and line.get("Affectation (nom)"):
                user.name = line["Affectation (nom)"]
            table = user.table_for(lecture)
            DBSession.add(table)
            table.amendements.append(amendement)
        previous_reponse = reponse
        reponses_count += 1

    return reponses_count, errors_count


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
