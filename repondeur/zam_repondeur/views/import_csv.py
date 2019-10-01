import csv
import io
from collections import Counter
from typing import BinaryIO, Dict, TextIO

from pyramid.httpexceptions import HTTPFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config

from zam_repondeur.message import Message
from zam_repondeur.models import Amendement, Lecture, Team
from zam_repondeur.models.events.lecture import ReponsesImportees
from zam_repondeur.resources import LectureResource
from zam_repondeur.services.import_export.common import import_amendement
from zam_repondeur.services.import_export.spreadsheet import column_name_to_field


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
            team=context.dossier_resource.dossier.team,
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
        ReponsesImportees.create(lecture=lecture, request=request)

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
    team: Team,
) -> Counter:
    previous_reponse = ""
    counter = Counter({"reponses": 0, "reponses_errors": 0})

    reponses_text_file = io.TextIOWrapper(reponses_file, encoding="utf-8-sig")

    delimiter = _guess_csv_delimiter(reponses_text_file)

    for line in csv.DictReader(reponses_text_file, delimiter=delimiter):
        item = {
            column_name_to_field(column_name): value
            for column_name, value in line.items()
            if column_name is not None
        }
        import_amendement(
            request, lecture, amendements, item, counter, previous_reponse, team
        )

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
