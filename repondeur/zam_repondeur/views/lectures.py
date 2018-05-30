import os
import re
from dataclasses import dataclass
from tempfile import NamedTemporaryFile
from typing import Any, Generator, List

from pyramid.httpexceptions import HTTPBadRequest, HTTPFound
from pyramid.request import Request
from pyramid.response import FileResponse, Response
from pyramid.view import view_config, view_defaults

from zam_aspirateur.amendements.models import Amendement
from zam_aspirateur.amendements.fetch import fetch_and_parse_all, NotFound
from zam_aspirateur.amendements.writer import write_csv, write_xlsx
from zam_aspirateur.__main__ import process_amendements


CHAMBRES = {"senat": "Sénat"}

SESSIONS = ["2017-2018"]


RE_TEXTE = re.compile(r"^(?P<chambre>\w+)-(?P<session>\d{4}-\d{4})-(?P<num_texte>\d+)$")


@dataclass
class Lecture:
    chambre: str
    session: str
    num_texte: str

    @property
    def chambre_disp(self) -> str:
        return CHAMBRES[self.chambre]

    def __str__(self) -> str:
        return f"{self.chambre_disp}, session {self.session}, texte nº {self.num_texte}"

    def __lt__(self, other: Any) -> bool:
        if type(self) != type(other):
            return NotImplemented
        return (self.chambre, self.session, int(self.num_texte)) < (
            other.chambre,
            other.session,
            int(other.num_texte),
        )


@view_config(route_name="lectures_list", renderer="lectures_list.html")
def lectures_list(request: Request) -> dict:
    return {
        "lectures": list(
            sorted(
                list_lectures(request.registry.settings["zam.data_dir"]), reverse=True
            )
        )
    }


def list_lectures(dirname: str) -> Generator:
    if not os.path.isdir(dirname):
        return
    for name in os.listdir(dirname):
        mo = RE_TEXTE.match(name)
        if mo is not None:
            yield Lecture(**mo.groupdict())  # type: ignore


@view_defaults(route_name="lectures_add", renderer="lectures_add.html")
class LecturesAdd:
    def __init__(self, request: Request) -> None:
        self.request = request
        self.data_dir = self.request.registry.settings["zam.data_dir"]

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

        lecture_dir = os.path.join(self.data_dir, f"{chambre}-{session}-{num_texte}")
        if os.path.isdir(lecture_dir):
            self.request.session.flash(("warning", "Cette lecture existe déjà..."))
        else:
            os.makedirs(lecture_dir)
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
        "lecture": Lecture(  # type: ignore
            chambre=request.matchdict["chambre"],
            session=request.matchdict["session"],
            num_texte=request.matchdict["num_texte"],
        )
    }


@view_config(route_name="amendements_csv")
def amendements_csv(request: Request) -> Response:
    chambre = request.matchdict["chambre"]
    session = request.matchdict["session"]
    num_texte = request.matchdict["num_texte"]
    assert chambre in CHAMBRES

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

        write_csv(amendements, tmp_file_path)

        response = FileResponse(tmp_file_path)
        attach_name = f"amendements-{chambre}-{session}-{num_texte}.csv"
        response.content_type = "text/csv"
        response.headers["Content-Disposition"] = f"attachment; filename={attach_name}"
        return response


@view_config(route_name="amendements_xlsx")
def amendements_xlsx(request: Request) -> Response:
    chambre = request.matchdict["chambre"]
    session = request.matchdict["session"]
    num_texte = request.matchdict["num_texte"]
    assert chambre in CHAMBRES

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

        write_xlsx(amendements, tmp_file_path)

        response = FileResponse(tmp_file_path)
        attach_name = f"amendements-{chambre}-{session}-{num_texte}.xlsx"
        response.content_type = (
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response.headers["Content-Disposition"] = f"attachment; filename={attach_name}"
        return response


def get_amendements_senat(session: str, num_texte: str) -> List[Amendement]:
    amendements = fetch_and_parse_all(session=session, num=num_texte)
    processed_amendements = process_amendements(
        amendements=amendements, session=session, num=num_texte
    )  # type: List[Amendement]
    return processed_amendements
