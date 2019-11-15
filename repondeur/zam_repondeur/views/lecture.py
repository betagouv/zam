from datetime import date

from pyramid.httpexceptions import HTTPFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config
from sqlalchemy.orm import load_only, noload

from zam_repondeur.message import Message
from zam_repondeur.models import DBSession, SharedTable
from zam_repondeur.resources import LectureResource
from zam_repondeur.tasks.fetch import fetch_amendements


@view_config(context=LectureResource, name="manual_refresh")
def manual_refresh(context: LectureResource, request: Request) -> Response:
    lecture = context.model()
    fetch_amendements(lecture.pk)
    # The progress is initialized even if the task is async for early feedback
    # to users and ability to disable the refresh button.
    # The total is doubled because we need to handle the dry_run.
    lecture.set_fetch_progress(1, len(lecture.amendements) * 2)
    request.session.flash(
        Message(cls="success", text="Rafraichissement des amendements en cours.")
    )
    amendements_collection = context["amendements"]
    return HTTPFound(location=request.resource_url(amendements_collection))


@view_config(context=LectureResource, name="journal", renderer="lecture_journal.html")
def lecture_journal(context: LectureResource, request: Request) -> Response:
    lecture = context.model(noload("amendements"))
    return {
        "lecture": lecture,
        "dossier_resource": context.dossier_resource,
        "lecture_resource": context,
        "current_tab": "journal",
        "today": date.today(),
        "settings": request.registry.settings,
    }


@view_config(context=LectureResource, name="options", renderer="lecture_options.html")
def lecture_options(context: LectureResource, request: Request) -> Response:
    lecture = context.model(noload("amendements"))
    shared_tables = (
        DBSession.query(SharedTable)
        .filter(SharedTable.lecture_pk == lecture.pk)
        .options(load_only("lecture_pk", "nb_amendements", "slug", "titre"))
    ).all()
    return {
        "lecture": lecture,
        "dossier_resource": context.dossier_resource,
        "lecture_resource": context,
        "current_tab": "options",
        "shared_tables": shared_tables,
    }


@view_config(context=LectureResource, name="progress_status", renderer="json")
def progress_status(context: LectureResource, request: Request) -> dict:
    lecture = context.model(noload("amendements"))
    return lecture.get_fetch_progress() or {}
