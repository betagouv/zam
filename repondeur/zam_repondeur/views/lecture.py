from datetime import date

from pyramid.httpexceptions import HTTPBadRequest, HTTPFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config
from sqlalchemy.orm import load_only, noload

from zam_repondeur.message import Message
from zam_repondeur.models import Amendement, DBSession, SharedTable
from zam_repondeur.resources import LectureResource
from zam_repondeur.tasks.fetch import fetch_amendements


@view_config(context=LectureResource, name="manual_refresh", permission="refresh")
def manual_refresh(context: LectureResource, request: Request) -> Response:
    lecture = context.model()
    amendements_collection = context["amendements"]
    if lecture.get_fetch_progress():
        request.session.flash(
            Message(
                cls="warning", text="Rafraîchissement des amendements déjà en cours."
            )
        )
        return HTTPFound(location=request.resource_url(amendements_collection))
    fetch_amendements(lecture.pk)
    # The progress is initialized even if the task is async for early feedback
    # to users and ability to disable the refresh button.
    # The total is doubled because we need to handle the dry_run.
    total = len(lecture.amendements) * 2 if lecture.amendements else 100
    lecture.set_fetch_progress(1, total)
    request.session.flash(
        Message(cls="success", text="Rafraîchissement des amendements en cours.")
    )
    return HTTPFound(location=request.resource_url(amendements_collection))


@view_config(context=LectureResource, name="journal", renderer="lecture_journal.html")
def lecture_journal(context: LectureResource, request: Request) -> Response:
    lecture = context.model(noload("amendements"))
    settings = request.registry.settings
    refreshable = lecture.refreshable_for(
        "articles", settings
    ) or lecture.refreshable_for("amendements", settings)
    can_refresh = request.has_permission("refresh", context)
    refreshing = lecture.get_fetch_progress()
    allowed_to_refresh = refreshable and can_refresh and not refreshing
    return {
        "lecture": lecture,
        "dossier_resource": context.dossier_resource,
        "lecture_resource": context,
        "current_tab": "journal",
        "today": date.today(),
        "allowed_to_refresh": allowed_to_refresh,
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


@view_config(context=LectureResource, name="search_amendement", renderer="json")
def search_amendement(context: LectureResource, request: Request) -> dict:
    lecture = context.model(noload("amendements"))

    try:
        num_param: str = request.params.get("num", "")
        num: int = int(num_param)
    except ValueError:
        raise HTTPBadRequest()

    amendement = (
        DBSession.query(Amendement)
        .filter(Amendement.lecture == lecture, Amendement.num == num)
        .first()
    )
    if amendement is None:
        raise HTTPBadRequest()

    total_count_amendements = lecture.nb_amendements
    max_amendements_for_full_index = int(
        request.registry.settings.get("zam.limits.max_amendements_for_full_index", 1000)
    )
    too_many_amendements = total_count_amendements > max_amendements_for_full_index

    result = {
        "index": request.resource_url(
            context["amendements"],
            query={
                "article": amendement.article.url_key if too_many_amendements else "all"
            },
            anchor=amendement.slug,
        ),
    }
    if amendement.is_displayable:
        result["visionneuse"] = request.resource_url(
            context["articles"][amendement.article.url_key],
            "reponses",
            anchor=amendement.slug,
        )
    return result
