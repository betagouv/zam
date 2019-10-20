from datetime import date

from pyramid.httpexceptions import HTTPFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config
from sqlalchemy.orm import load_only, noload

from zam_repondeur.message import Message
from zam_repondeur.models import DBSession, SharedTable
from zam_repondeur.resources import LectureResource
from zam_repondeur.tasks.fetch import fetch_amendements, fetch_articles


@view_config(context=LectureResource, name="manual_refresh")
def manual_refresh(context: LectureResource, request: Request) -> Response:
    lecture = context.model()
    fetch_amendements(lecture.pk)
    fetch_articles(lecture.pk)
    request.session.flash(
        Message(
            cls="success",
            text="Rafraichissement des amendements et des articles en cours.",
        )
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
