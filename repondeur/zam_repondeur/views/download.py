import os
from tempfile import NamedTemporaryFile

from pyramid.httpexceptions import HTTPBadRequest
from pyramid.request import Request
from pyramid.response import FileResponse, Response
from pyramid.view import view_config
from sqlalchemy.orm import joinedload

from zam_repondeur.resources import AmendementResource, LectureResource
from zam_repondeur.writer import write_csv, write_pdf, write_pdf1, write_xlsx


DOWNLOAD_FORMATS = {
    "csv": (write_csv, "text/csv"),
    "pdf": (write_pdf, "application/pdf"),
    "xlsx": (
        write_xlsx,
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ),
}


@view_config(context=LectureResource, name="download_amendements")
def download_amendements(context: LectureResource, request: Request) -> Response:

    fmt: str = request.params.get("format", "")
    if fmt not in ("csv", "xlsx", "pdf"):
        raise HTTPBadRequest(f'Invalid value "{fmt}" for "format" param')

    if fmt == "pdf":
        options = [
            joinedload("articles").joinedload("amendements").joinedload("children")
        ]
    else:
        options = [joinedload("articles")]

    lecture = context.model(*options)

    with NamedTemporaryFile() as file_:

        tmp_file_path = os.path.abspath(file_.name)

        write_func, content_type = DOWNLOAD_FORMATS[fmt]

        write_func(lecture, tmp_file_path, request)

        response = FileResponse(tmp_file_path)
        attach_name = (
            f"amendements-{lecture.chambre}-{lecture.session}-{lecture.num_texte}-"
            f"{lecture.organe}.{fmt}"
        )
        response.content_type = content_type
        response.headers["Content-Disposition"] = f"attachment; filename={attach_name}"
        return response


@view_config(context=AmendementResource, name="download_amendement")
def download_amendement(context: AmendementResource, request: Request) -> Response:
    amendement = context.model()
    lecture = amendement.lecture

    with NamedTemporaryFile() as file_:
        tmp_file_path = os.path.abspath(file_.name)
        write_pdf1(lecture, amendement, tmp_file_path, request)
        response = FileResponse(tmp_file_path)
        attach_name = (
            f"amendement-{amendement.num}-"
            f"{lecture.chambre}-{lecture.session}-{lecture.num_texte}-"
            f"{lecture.organe}.pdf"
        )
        response.content_type = "application/pdf"
        response.headers["Content-Disposition"] = f"attachment; filename={attach_name}"
        return response
