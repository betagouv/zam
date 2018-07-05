import os
from tempfile import NamedTemporaryFile

from pyramid.httpexceptions import HTTPBadRequest
from pyramid.request import Request
from pyramid.response import FileResponse, Response
from pyramid.view import view_config
from sqlalchemy.sql.expression import case

from zam_aspirateur.amendements.writer import write_csv, write_xlsx

from zam_repondeur.models import DBSession, Amendement, CHAMBRES


DOWNLOAD_FORMATS = {
    "csv": (write_csv, "text/csv"),
    "xlsx": (
        write_xlsx,
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ),
}


@view_config(route_name="download_amendements")
def download_amendements(request: Request) -> Response:
    chambre = request.matchdict["chambre"]
    session = request.matchdict["session"]
    num_texte = int(request.matchdict["num_texte"])
    organe = request.matchdict["organe"]
    fmt = request.matchdict["format"]

    if chambre not in CHAMBRES:
        return HTTPBadRequest(f'Invalid value "{chambre}" for "chambre" param')

    amendements = (
        DBSession.query(Amendement)
        .filter(
            Amendement.chambre == chambre,
            Amendement.session == session,
            Amendement.num_texte == num_texte,
            Amendement.organe == organe,
        )
        .order_by(
            case([(Amendement.position.is_(None), 1)], else_=0),
            Amendement.position,
            Amendement.num,
        )
        .all()
    )

    with NamedTemporaryFile() as file_:

        tmp_file_path = os.path.abspath(file_.name)

        write_func, content_type = DOWNLOAD_FORMATS[fmt]

        write_func(amendements, tmp_file_path)

        response = FileResponse(tmp_file_path)
        attach_name = f"amendements-{chambre}-{session}-{num_texte}.{fmt}"
        response.content_type = content_type
        response.headers["Content-Disposition"] = f"attachment; filename={attach_name}"
        return response
