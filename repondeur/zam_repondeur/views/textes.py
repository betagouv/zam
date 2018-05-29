import os
import re
from dataclasses import dataclass
from typing import Generator, List

from pyramid.httpexceptions import HTTPBadRequest, HTTPFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config, view_defaults

from zam_aspirateur.amendements.models import Amendement
from zam_aspirateur.amendements.fetch import fetch_and_parse_all
from zam_aspirateur.__main__ import process_amendements


CHAMBRES = {"senat": "Sénat"}

SESSIONS = ["2017-2018"]


RE_TEXTE = re.compile(r"^(?P<chambre>\w+)-(?P<session>\d{4}-\d{4})-(?P<num_texte>\d+)$")


@dataclass
class Texte:
    chambre: str
    session: str
    num_texte: str

    @property
    def chambre_disp(self) -> str:
        return CHAMBRES[self.chambre]

    def __str__(self) -> str:
        return f"{self.chambre_disp}, session {self.session}, texte nº {self.num_texte}"


@view_config(route_name="textes_list", renderer="textes_list.html")
def textes_list(request: Request) -> dict:
    return {"textes": list(list_textes(request.registry.settings["zam.data_dir"]))}


def list_textes(dirname: str) -> Generator:
    if not os.path.isdir(dirname):
        return
    for name in os.listdir(dirname):
        mo = RE_TEXTE.match(name)
        if mo is not None:
            yield Texte(**mo.groupdict())  # type: ignore


@view_defaults(route_name="textes_add", renderer="textes_add.html")
class TextesAdd:
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
        if chambre != "senat":
            raise HTTPBadRequest
        basename = f"{chambre}-{session}-{num_texte}"
        os.makedirs(os.path.join(self.data_dir, basename), exist_ok=True)
        return HTTPFound(location=self.request.route_url("textes_list"))

    def _form_data(self) -> dict:
        return {
            "chambres": CHAMBRES.items(),
            "sessions": [(sess, sess) for sess in SESSIONS],
        }


def get_amendements_senat(session: str, num_texte: str) -> List[Amendement]:
    amendements = fetch_and_parse_all(session=session, num=num_texte)
    processed_amendements = process_amendements(
        amendements=amendements, session=session, num=num_texte
    )  # type: List[Amendement]
    return processed_amendements
