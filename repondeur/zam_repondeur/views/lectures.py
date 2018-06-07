import os
from tempfile import NamedTemporaryFile
from typing import List

from pyramid.httpexceptions import HTTPBadRequest, HTTPFound
from pyramid.request import Request
from pyramid.response import FileResponse, Response
from pyramid.view import view_config, view_defaults

from zam_aspirateur.amendements.models import Amendement
from zam_aspirateur.amendements.fetch_senat import fetch_and_parse_all, NotFound
from zam_aspirateur.amendements.writer import write_csv, write_xlsx
from zam_aspirateur.__main__ import process_amendements

from zam_repondeur.models import Lecture, CHAMBRES, SESSIONS


@view_config(route_name="lectures_list", renderer="lectures_list.html")
def lectures_list(request: Request) -> dict:
    return {"lectures": Lecture.all()}


@view_defaults(route_name="lectures_add", renderer="lectures_add.html")
class LecturesAdd:
    def __init__(self, request: Request) -> None:
        self.request = request

    @view_config(request_method="GET")
    def get(self) -> dict:
        return self._form_data()

    @view_config(request_method="POST")
    def post(self) -> Response:
        chambre = self.request.POST["chambre"]
        session = self.request.POST["session"]
        num_texte = self.request.POST["num_texte"]
        if chambre not in CHAMBRES:
            raise HTTPBadRequest

        if Lecture.exists(chambre, session, num_texte):
            self.request.session.flash(("warning", "Cette lecture existe déjà..."))
        else:
            Lecture.create(chambre, session, num_texte)
            self.request.session.flash(("success", "Lecture créée avec succès."))

        return HTTPFound(
            location=self.request.route_url(
                "lecture", chambre=chambre, session=session, num_texte=num_texte
            )
        )

    def _form_data(self) -> dict:
        return {
            "chambres": CHAMBRES.items(),
            "sessions": [(sess, sess) for sess in SESSIONS],
        }


@view_config(route_name="lecture", renderer="lecture.html")
def lecture(request: Request) -> dict:
    return {
        "lecture": Lecture(
            chambre=request.matchdict["chambre"],
            session=request.matchdict["session"],
            num_texte=request.matchdict["num_texte"],
        )
    }


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

    try:
        amendements = get_amendements_senat(session, num_texte)
    except NotFound:
        request.session.flash(("danger", "Aucun amendement n'a pu être trouvé."))
        return HTTPFound(
            location=request.route_url(
                "lecture", chambre=chambre, session=session, num_texte=num_texte
            )
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


def get_amendements_senat(session: str, num_texte: str) -> List[Amendement]:
    amendements = fetch_and_parse_all(session=session, num=num_texte)
    processed_amendements = process_amendements(
        amendements=amendements, session=session, num=num_texte
    )  # type: List[Amendement]
    return processed_amendements
