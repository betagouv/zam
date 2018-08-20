from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config

from zam_repondeur.resources import LectureResource


@view_config(context=LectureResource, name="journal", renderer="journal.html")
def journal(context: LectureResource, request: Request) -> Response:
    lecture = context.model()
    return {"lecture": lecture, "journal": lecture.journal}
