import os
from tempfile import NamedTemporaryFile
from typing import List

from pyramid.httpexceptions import HTTPBadRequest
from pyramid.request import Request
from pyramid.response import FileResponse, Response
from pyramid.view import view_config
from sqlalchemy.orm import joinedload, load_only, subqueryload

from zam_repondeur.export.pdf import write_pdf, write_pdf_multiple
from zam_repondeur.models import Batch
from zam_repondeur.resources import LectureResource
from zam_repondeur.services.import_export.json import export_json
from zam_repondeur.services.import_export.spreadsheet import write_xlsx

DOWNLOAD_FORMATS = {
    "json": (export_json, "application/json"),
    "pdf": (write_pdf, "application/pdf"),
    "xlsx": (
        write_xlsx,
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ),
}


AMDT_OPTIONS = [
    joinedload("user_content"),
    joinedload("user_table").joinedload("user").load_only("email", "name"),
    joinedload("article").options(
        load_only("lecture_pk", "mult", "num", "pos", "type"),
        joinedload("user_content"),
    ),
]

EXPORT_OPTIONS = [subqueryload("amendements").options(*AMDT_OPTIONS)]

PDF_OPTIONS = [
    joinedload("dossier").load_only("titre"),
    subqueryload("articles").options(
        joinedload("user_content"),
        subqueryload("amendements").options(
            subqueryload("children"),
            joinedload("user_content").defer("comments"),
            *AMDT_OPTIONS,
        ),
    ),
]


@view_config(context=LectureResource, name="download_amendements")
def download_amendements(context: LectureResource, request: Request) -> Response:

    fmt: str = request.params.get("format", "")
    if fmt not in DOWNLOAD_FORMATS.keys():
        raise HTTPBadRequest(f'Invalid value "{fmt}" for "format" param')

    if fmt == "pdf":
        options = PDF_OPTIONS
    else:
        options = EXPORT_OPTIONS

    lecture = context.model(*options)

    with NamedTemporaryFile() as file_:

        tmp_file_path = os.path.abspath(file_.name)

        write_func, content_type = DOWNLOAD_FORMATS[fmt]

        write_func(lecture, tmp_file_path, request)

        response = FileResponse(tmp_file_path)
        attach_name = (
            f"lecture-{lecture.chambre}-{lecture.texte.numero}-"
            f"{lecture.organe}.{fmt}"
        )
        response.content_type = content_type
        response.headers["Content-Disposition"] = f"attachment; filename={attach_name}"
        return response


@view_config(context=LectureResource, name="export_pdf")
def export_pdf(context: LectureResource, request: Request) -> Response:

    lecture = context.model(*PDF_OPTIONS)

    try:
        nums: List[int] = [int(num) for num in request.params.getall("nums")]
    except ValueError:
        raise HTTPBadRequest()

    amendements = [
        amendement
        for amendement in (lecture.find_amendement(num) for num in nums)
        if amendement is not None
    ]
    expanded_amendements = list(Batch.expanded_batches(amendements))

    with NamedTemporaryFile() as file_:

        tmp_file_path = os.path.abspath(file_.name)

        write_pdf_multiple(
            lecture=lecture,
            amendements=amendements,
            filename=tmp_file_path,
            request=request,
        )

        response = FileResponse(tmp_file_path)
        attach_name = (
            f"amendement{'s' if len(expanded_amendements) > 1 else ''}-"
            f"{','.join(str(amdt.num) for amdt in expanded_amendements)}-"
            f"{lecture.chambre}-{lecture.texte.numero}-"
            f"{lecture.organe}.pdf"
        )
        response.content_type = "application/pdf"
        response.headers["Content-Disposition"] = f"attachment; filename={attach_name}"
        return response
