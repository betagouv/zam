import os
from tempfile import NamedTemporaryFile

from pyramid.httpexceptions import HTTPBadRequest
from pyramid.request import Request
from pyramid.response import FileResponse, Response
from pyramid.view import view_config
from sqlalchemy.sql.expression import case
from sqlalchemy.orm import joinedload

from zam_repondeur.models import DBSession, Amendement
from zam_repondeur.resources import LectureResource
from zam_repondeur.writer import write_csv, write_pdf, write_xlsx


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
    lecture = context.model()

    amendements = (
        DBSession.query(Amendement)
        .filter(
            Amendement.chambre == lecture.chambre,
            Amendement.session == lecture.session,
            Amendement.num_texte == lecture.num_texte,
            Amendement.organe == lecture.organe,
        )
        .order_by(
            case([(Amendement.position.is_(None), 1)], else_=0),  # type: ignore
            Amendement.position,
            Amendement.num,
        )
        .options(joinedload(Amendement.parent))  # type: ignore
        .all()
    )

    fmt: str = request.params.get("format", "")
    if fmt not in ("csv", "xlsx", "pdf"):
        raise HTTPBadRequest(f'Invalid value "{fmt}" for "format" param')

    with NamedTemporaryFile() as file_:

        tmp_file_path = os.path.abspath(file_.name)

        write_func, content_type = DOWNLOAD_FORMATS[fmt]

        write_func(lecture, amendements, tmp_file_path, request)

        response = FileResponse(tmp_file_path)
        attach_name = (
            f"amendements-{lecture.chambre}-{lecture.session}-{lecture.num_texte}-"
            f"{lecture.organe}.{fmt}"
        )
        response.content_type = content_type
        response.headers["Content-Disposition"] = f"attachment; filename={attach_name}"
        return response
