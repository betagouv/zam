import logging
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from pyramid.httpexceptions import HTTPFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config

from zam_repondeur.fetch.an.liasse_xml import import_liasse_xml
from zam_repondeur.message import Message
from zam_repondeur.models import DBSession, Journal
from zam_repondeur.resources import LectureResource


logger = logging.getLogger(__name__)


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

    # Backup uploaded file to make troubleshooting easier
    backup_path = get_backup_path(request)
    if backup_path is not None:
        save_uploaded_file(liasse_field, backup_path)

    try:
        amendements, errors = import_liasse_xml(liasse_field.file)
    except ValueError:
        logger.exception("Erreur d'import de la liasse XML")
        request.session.flash(
            Message(cls="danger", text="Le format du fichier n’est pas valide.")
        )
        return

    if errors:
        if len(errors) == 1:
            what = "l'amendement"
        else:
            what = "les amendements"
        uids = ", ".join(uid for uid, cause in errors)
        request.session.flash(
            Message(cls="warning", text=f"Impossible d'importer {what} {uids}.")
        )

    if len(amendements) == 0:
        request.session.flash(
            Message(
                cls="warning",
                text="Aucun amendement valide n’a été trouvé dans ce fichier.",
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


def get_backup_path(request: Request) -> Optional[Path]:
    backup_dir: Optional[str] = request.registry.settings.get("zam.uploads_backup_dir")
    if not backup_dir:
        return None
    backup_path = Path(backup_dir)
    backup_path.mkdir(parents=True, exist_ok=True)
    return backup_path


def save_uploaded_file(form_field: Any, backup_dir: Path) -> None:
    form_field.file.seek(0)
    timestamp = datetime.utcnow().isoformat(timespec="seconds")
    sanitized_filename = os.path.basename(form_field.filename)
    backup_filename = Path(backup_dir) / f"liasse-{timestamp}-{sanitized_filename}"
    with backup_filename.open("wb") as backup_file:
        shutil.copyfileobj(form_field.file, backup_file)
    logger.info("Uploaded file saved to %s", backup_filename)
    form_field.file.seek(0)
