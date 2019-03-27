import os
from tempfile import NamedTemporaryFile
from typing import List

from pyramid.httpexceptions import HTTPBadRequest
from pyramid.request import Request
from pyramid.response import FileResponse, Response
from pyramid.view import view_config
from sqlalchemy.orm import joinedload

from zam_repondeur.resources import LectureResource
from zam_repondeur.export.pdf import write_pdf, write_pdf_multiple
from zam_repondeur.export.spreadsheet import write_xlsx


DOWNLOAD_FORMATS = {
    "pdf": (write_pdf, "application/pdf"),
    "xlsx": (
        write_xlsx,
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ),
}


@view_config(context=LectureResource, name="download_amendements")
def download_amendements(context: LectureResource, request: Request) -> Response:

    fmt: str = request.params.get("format", "")
    if fmt not in DOWNLOAD_FORMATS.keys():
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
            f"lecture-{lecture.chambre}-{lecture.session}-{lecture.num_texte}-"
            f"{lecture.organe}.{fmt}"
        )
        response.content_type = content_type
        response.headers["Content-Disposition"] = f"attachment; filename={attach_name}"
        return response


@view_config(context=LectureResource, name="export_pdf")
def export_pdf(context: LectureResource, request: Request) -> Response:

    lecture = context.model(
        joinedload("articles").joinedload("amendements").joinedload("children")
    )

    try:
        nums: List[int] = [int(num) for num in request.params.getall("nums")]
    except ValueError:
        raise HTTPBadRequest()

    amendements = [
        amendement
        for amendement in (lecture.find_amendement(num) for num in nums)
        if amendement is not None
    ]

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
            f"amendement{'s' if len(nums) > 1 else ''}-"
            f"{','.join(str(num) for num in nums)}-"
            f"{lecture.chambre}-{lecture.session}-{lecture.num_texte}-"
            f"{lecture.organe}.pdf"
        )
        response.content_type = "application/pdf"
        response.headers["Content-Disposition"] = f"attachment; filename={attach_name}"
        return response
