from typing import List

from pyramid.httpexceptions import HTTPBadRequest
from pyramid.request import Request
from pyramid.view import view_config, view_defaults

from zam_aspirateur.amendements.models import Amendement
from zam_aspirateur.amendements.fetch import fetch_and_parse_all
from zam_aspirateur.__main__ import process_amendements


CHAMBRES = {"senat": "Sénat"}

SESSIONS = ["2017-2018"]


@view_defaults(route_name="textes_add", renderer="textes_add.html")
class TextesAdd:
    def __init__(self, request: Request) -> None:
        self.request = request

    @view_config(request_method="GET")
    def get(self) -> dict:
        return self._form_data()

    @view_config(request_method="POST")
    def post(self) -> dict:
        chambre = self.request.POST["chambre"]
        session = self.request.POST["session"]
        num_texte = self.request.POST["num_texte"]
        if chambre != "senat":
            raise HTTPBadRequest
        res = self._form_data()
        res.update({"amendements": get_amendements_senat(session, num_texte)})
        return res

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
