import logging
from json import load
from typing import Dict, Iterator, List, NamedTuple, Optional

from ...dates import parse_date
from ..common import extract_from_remote_zip, roman
from .models import ChambreRef, LectureRef, DossierRef, TexteRef, TypeTexte


logger = logging.getLogger(__name__)


def get_dossiers_legislatifs(*legislatures: int) -> Dict[str, DossierRef]:
    dossiers: Dict[str, DossierRef] = {}
    for legislature in legislatures:
        dossiers.update(_get_dossiers_legislatifs(legislature))
    return dossiers


def _get_dossiers_legislatifs(legislature: int) -> Dict[str, DossierRef]:
    data = fetch_dossiers_legislatifs(legislature)
    textes = parse_textes(data["export"])
    dossiers = parse_dossiers(data["export"], textes)
    return dossiers


def fetch_dossiers_legislatifs(legislature: int) -> dict:
    legislature_roman = roman(legislature)
    filename = f"Dossiers_Legislatifs_{legislature_roman}.json"
    url = f"http://data.assemblee-nationale.fr/static/openData/repository/{legislature}/loi/dossiers_legislatifs/{filename}.zip"  # noqa
    with extract_from_remote_zip(url, filename) as json_file:
        data: dict = load(json_file)
    return data


def parse_textes(export: dict) -> Dict[str, TexteRef]:
    return {
        item["uid"]: TexteRef(
            uid=item["uid"],
            type_=type_texte(item),
            chambre=chambre_texte(item),
            legislature=legislature_texte(item),
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


def chambre_texte(item: dict) -> ChambreRef:
    if item["uid"][4:6] == "AN":
        return ChambreRef.AN
    if item["uid"][4:6] == "SN":
        return ChambreRef.SENAT
    raise NotImplementedError


def legislature_texte(item: dict) -> Optional[int]:
    legislature = item["legislature"]
    if not legislature:
        return None
    return int(legislature)


def parse_dossiers(export: dict, textes: Dict[str, TexteRef]) -> Dict[str, DossierRef]:
    dossier_dicts = (
        item["dossierParlementaire"]
        for item in export["dossiersLegislatifs"]["dossier"]
        if isinstance(item, dict)
    )
    dossier_models = []
    for dossier_dict in dossier_dicts:
        if is_dossier(dossier_dict):
            dossier_models.append(parse_dossier(dossier_dict, textes))
    return {dossier.uid: dossier for dossier in dossier_models}


def is_dossier(data: dict) -> bool:
    # Some records don't have a type field, so we have to rely on the UID as a fall-back
    return _has_dossier_type(data) or _has_dossier_uid(data)


def _has_dossier_type(data: dict) -> bool:
    return data.get("@xsi:type") == "DossierLegislatif_Type"


def _has_dossier_uid(data: dict) -> bool:
    uid: str = data["uid"]
    return uid.startswith("DLR")


TOP_LEVEL_ACTES = {
    "AN1": (ChambreRef.AN, "Première lecture"),
    "SN1": (ChambreRef.SENAT, "Première lecture"),
    "ANNLEC": (ChambreRef.AN, "Nouvelle lecture"),
    "SNNLEC": (ChambreRef.SENAT, "Nouvelle lecture"),
    "ANLDEF": (ChambreRef.AN, "Lecture définitive"),
}


def parse_dossier(dossier: dict, textes: Dict[str, TexteRef]) -> DossierRef:
    uid = dossier["uid"]
    titre = dossier["titreDossier"]["titre"]
    is_plf = "PLF" in dossier
    lectures = [
        lecture
        for acte in top_level_actes(dossier)
        for lecture in gen_lectures(acte, textes, is_plf)
    ]
    return DossierRef(uid=uid, titre=titre, lectures=lectures)


def top_level_actes(dossier: dict) -> Iterator[dict]:
    for acte in extract_actes(dossier):
        if acte["codeActe"] in TOP_LEVEL_ACTES:
            yield acte


def gen_lectures(
    acte: dict, textes: Dict[str, TexteRef], is_plf: bool = False
) -> Iterator[LectureRef]:
    for result in walk_actes(acte):
        chambre, titre = TOP_LEVEL_ACTES[acte["codeActe"]]
        if result.phase == "COM-FOND":
            titre += " – Commission saisie au fond"
        elif result.phase == "COM-AVIS":
            titre += " – Commission saisie pour avis"
        elif result.phase == "DEBATS":
            titre += " – Séance publique"
        else:
            raise NotImplementedError

        texte = textes[result.texte]

        # The 1st "lecture" of the "projet de loi de finances" (PLF) has two parts
        parties: List[Optional[int]] = [
            1,
            2,
        ] if is_plf and result.premiere_lecture else [None]

        for partie in parties:
            yield LectureRef(
                chambre=chambre,
                titre=titre,
                texte=texte,
                partie=partie,
                organe=result.organe,
            )


class WalkResult(NamedTuple):
    phase: str
    organe: str
    texte: str
    premiere_lecture: bool


def walk_actes(acte: dict) -> Iterator[WalkResult]:
    current_texte = None

    def _walk_actes(acte: dict) -> Iterator[WalkResult]:
        nonlocal current_texte

        code = acte["codeActe"]
        premiere_lecture = code.startswith("AN1") or code.startswith("SN1")
        phase = code.split("-", 1)[1] if "-" in code else ""

        if phase in {"COM-FOND", "COM-AVIS", "DEBATS"}:
            if current_texte is not None:
                yield WalkResult(
                    phase=phase,
                    organe=acte["organeRef"],
                    texte=current_texte,
                    premiere_lecture=premiere_lecture,
                )
            else:
                logger.warning(f"Could not match a text for {acte['uid']}")

        for key in ["texteAssocie", "texteAdopte"]:
            if key in acte and acte[key] is not None:
                uid = acte[key]
                if uid[:4] in {"PRJL", "PION"}:
                    current_texte = uid

        for sous_acte in extract_actes(acte):
            yield from _walk_actes(sous_acte)

    yield from _walk_actes(acte)


def extract_actes(acte: dict) -> List[dict]:
    children = (acte.get("actesLegislatifs") or {}).get("acteLegislatif", [])
    if isinstance(children, list):
        return children
    else:
        return [children]
