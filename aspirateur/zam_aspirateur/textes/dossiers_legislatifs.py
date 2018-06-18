from contextlib import contextmanager
from datetime import date
from io import BytesIO, TextIOWrapper
from json import load
from typing import Dict, Generator, IO
from zipfile import ZipFile

from ..http import cached_session
from .models import Chambre, Lecture, Dossier, Texte, TypeTexte


def get_dossiers_legislatifs(legislature: int) -> Dict[str, Dossier]:
    legislature_roman = roman(legislature)
    filename = f"Dossiers_Legislatifs_{legislature_roman}.json"
    url = f"http://data.assemblee-nationale.fr/static/openData/repository/{legislature}/loi/dossiers_legislatifs/{filename}.zip"  # noqa
    with extract_from_remote_zip(url, filename) as json_file:
        data = load(json_file)
    textes = parse_textes(data["export"])
    dossiers = parse_dossiers(data["export"], textes)
    return dossiers


def roman(n: int) -> str:
    if n == 15:
        return "XV"
    if n == 14:
        return "XIV"
    raise NotImplementedError


@contextmanager
def extract_from_remote_zip(url: str, filename: str) -> Generator[IO[str], None, None]:
    response = cached_session.get(url)
    assert response.headers["content-type"] == "application/zip"
    with ZipFile(BytesIO(response.content)) as zip_file:
        with zip_file.open(filename) as file_:
            yield TextIOWrapper(file_, encoding="utf-8")


def parse_textes(export: dict) -> Dict[str, Texte]:
    return {
        item["uid"]: Texte(  # type: ignore
            uid=item["uid"],
            type_=type_texte(item),
            numero=int(item["notice"]["numNotice"]),
            titre_long=item["titres"]["titrePrincipal"],
            titre_court=item["titres"]["titrePrincipalCourt"],
            date_depot=parse_date(item["cycleDeVie"]["chrono"]["dateDepot"]),
        )
        for item in export["textesLegislatifs"]["document"]
        if item["@xsi:type"] == "texteLoi_Type"
        if item["classification"]["type"]["code"] in {"PION", "PRJL"}
    }


def type_texte(item: dict) -> TypeTexte:
    code = item["classification"]["type"]["code"]
    if code == "PION":
        return TypeTexte.PROPOSITION
    if code == "PRJL":
        return TypeTexte.PROJET
    raise NotImplementedError


def parse_date(rfc339_datetime_string: str) -> date:
    return date(
        year=int(rfc339_datetime_string[0:4]),
        month=int(rfc339_datetime_string[5:7]),
        day=int(rfc339_datetime_string[8:10]),
    )


def parse_dossiers(export: dict, textes: Dict[str, Texte]) -> Dict[str, Dossier]:
    dossier_dicts = (
        item["dossierParlementaire"]
        for item in export["dossiersLegislatifs"]["dossier"]
    )
    dossier_models = (
        parse_dossier(dossier_dict, textes)
        for dossier_dict in dossier_dicts
        if dossier_dict["@xsi:type"] == "DossierLegislatif_Type"
    )
    return {dossier.uid: dossier for dossier in dossier_models}


CODES_ACTES = {
    "AN1": (Chambre.AN, "Première lecture"),
    "SN1": (Chambre.SENAT, "Première lecture"),
    "ANNLEC": (Chambre.AN, "Nouvelle lecture"),
    "SNNLEC": (Chambre.SENAT, "Nouvelle lecture"),
    "ANLDEF": (Chambre.AN, "Lecture définitive"),
}


def parse_dossier(dossier: dict, textes: Dict[str, Texte]) -> Dossier:
    actes = dossier["actesLegislatifs"]["acteLegislatif"]
    if isinstance(actes, dict):
        actes = [actes]
    lectures = (
        make_lecture(acte, textes) for acte in actes if acte["codeActe"] in CODES_ACTES
    )
    return Dossier(  # type: ignore
        uid=dossier["uid"],
        titre=dossier["titreDossier"]["titre"],
        lectures={lecture.texte.uid: lecture for lecture in lectures},
    )


def make_lecture(acte: dict, textes: Dict[str, Texte]) -> Lecture:
    chambre, titre = CODES_ACTES[acte["codeActe"]]
    textes_associes = [
        sous_acte["texteAssocie"]
        for sous_acte in acte["actesLegislatifs"]["acteLegislatif"]
        if sous_acte["@xsi:type"]
        in {"DepotInitiative_Type", "DepotInitiativeNavette_Type"}
        if "texteAssocie" in sous_acte
    ]
    assert len(textes_associes) == 1, textes_associes
    texte = textes[textes_associes[0]]
    return Lecture(chambre=chambre, titre=titre, texte=texte)  # type: ignore
