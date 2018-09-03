from datetime import datetime

from pyramid.httpexceptions import HTTPFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config

from zam_repondeur.fetch.an.liasse_xml import import_liasse_xml
from zam_repondeur.message import Message
from zam_repondeur.models import DBSession, Journal
from zam_repondeur.resources import LectureResource


@view_config(context=LectureResource, name="import_liasse_xml")
def upload_liasse_xml(context: LectureResource, request: Request) -> Response:
    _do_upload_liasse_xml(context, request)
    return HTTPFound(location=request.resource_url(context, "amendements"))


def _do_upload_liasse_xml(context: LectureResource, request: Request) -> Response:
    try:
        liasse_field = request.POST["liasse"]
    except KeyError:
        request.session.flash(
            Message(cls="warning", text="Veuillez d’abord sélectionner un fichier")
        )
        return

    if liasse_field == b"":
        request.session.flash(
            Message(cls="warning", text="Veuillez d’abord sélectionner un fichier")
        )
        return

    try:
        amendements = import_liasse_xml(liasse_field.file)
    except ValueError:
        request.session.flash(
            Message(cls="danger", text="Le format du fichier n’est pas valide.")
        )
        return

    if len(amendements) == 0:
        request.session.flash(
            Message(
                cls="warning", text="Aucun amendement n’a été trouvé dans ce fichier."
            )
        )
        return

    lecture = context.model()
    filtered_amendements = [
        amendement for amendement in amendements if amendement.lecture == lecture
    ]
    ignored = len(amendements) - len(filtered_amendements)

    if len(filtered_amendements) == 0:
        amendement = amendements[0]
        request.session.flash(
            Message(
                cls="danger",
                text=(
                    f"La liasse correspond à une autre lecture"
                    f" ({amendement.lecture})."
                ),
            )
        )
        return

    if ignored > 0:
        request.session.flash(
            Message(
                cls="warning",
                text=f"{ignored} amendements ignorés car non liés à cette lecture.",
            )
        )
    if len(amendements):
        if len(amendements) == 1:
            message = "1 nouvel amendement récupéré (import liasse XML)."
        else:
            message = (
                f"{len(amendements)} nouveaux amendements récupérés "
                "(import liasse XML)."
            )
        request.session.flash(Message(cls="success", text=message))
        Journal.create(lecture=lecture, kind="success", message=message)
        lecture.modified_at = datetime.utcnow()
        DBSession.add(lecture)
