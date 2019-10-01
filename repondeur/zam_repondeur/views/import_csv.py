from pyramid.httpexceptions import HTTPFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config

from zam_repondeur.message import Message
from zam_repondeur.models.events.lecture import ReponsesImportees
from zam_repondeur.resources import LectureResource
from zam_repondeur.services.import_export.csv import CSVError, import_csv


@view_config(context=LectureResource, name="import_csv", request_method="POST")
def upload_csv(context: LectureResource, request: Request) -> Response:

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
        counter = import_csv(
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
