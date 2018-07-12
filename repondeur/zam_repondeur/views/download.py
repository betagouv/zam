import os
from tempfile import NamedTemporaryFile

from pyramid.httpexceptions import HTTPNotFound
from pyramid.request import Request
from pyramid.response import FileResponse, Response
from pyramid.view import view_config
from sqlalchemy.sql.expression import case

from zam_repondeur.models import DBSession, Amendement, Lecture
from zam_repondeur.writer import write_csv, write_pdf, write_xlsx


DOWNLOAD_FORMATS = {
    "csv": (write_csv, "text/csv"),
    "pdf": (write_pdf, "application/pdf"),
    "xlsx": (
        write_xlsx,
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ),
}


@view_config(route_name="download_amendements")
def download_amendements(request: Request) -> Response:
    lecture = Lecture.get(
        chambre=request.matchdict["chambre"],
        session=request.matchdict["session"],
        num_texte=int(request.matchdict["num_texte"]),
        organe=request.matchdict["organe"],
    )
    if lecture is None:
        raise HTTPNotFound

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
        .all()
    )
    fmt = request.matchdict["format"]
    title = str(lecture)

    with NamedTemporaryFile() as file_:

        tmp_file_path = os.path.abspath(file_.name)

        write_func, content_type = DOWNLOAD_FORMATS[fmt]

        write_func(title, amendements, tmp_file_path, request)

        response = FileResponse(tmp_file_path)
        attach_name = (
            f"amendements-{lecture.chambre}-{lecture.session}-{lecture.num_texte}-"
            f"{lecture.organe}.{fmt}"
        )
        response.content_type = content_type
        response.headers["Content-Disposition"] = f"attachment; filename={attach_name}"
        return response
