import os
from tempfile import NamedTemporaryFile

from pyramid.httpexceptions import HTTPBadRequest
from pyramid.request import Request
from pyramid.response import FileResponse, Response
from pyramid.view import view_config

from zam_aspirateur.amendements.writer import write_csv, write_xlsx

from zam_repondeur.models import DBSession, Amendement as AmendementModel, CHAMBRES


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
    num_texte = request.matchdict["num_texte"]
    fmt = request.matchdict["format"]

    if chambre not in CHAMBRES:
        return HTTPBadRequest(f'Invalid value "{chambre}" for "chambre" param')

    amendements = (
        DBSession.query(AmendementModel)
        .filter(
            AmendementModel.chambre == chambre,
            AmendementModel.session == session,
            AmendementModel.num_texte == num_texte,
        )
        .order_by(AmendementModel.position, AmendementModel.num)
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
