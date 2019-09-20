import logging
from json import load
from typing import Any, Dict, Iterator, List, NamedTuple, Optional, Tuple

from zam_repondeur.models.chambre import Chambre
from zam_repondeur.slugs import slugify

from ...dates import parse_date
from ..common import extract_from_remote_zip, roman
from .models import DossierRef, DossierRefsByUID, LectureRef, TexteRef, TypeTexte

logger = logging.getLogger(__name__)


def get_dossiers_legislatifs_and_textes(
    *legislatures: int
) -> Tuple[DossierRefsByUID, Dict[str, TexteRef]]:
    all_dossiers: DossierRefsByUID = {}
    all_textes: Dict[str, TexteRef] = {}
    for legislature in legislatures:
        dossiers, textes = _get_dossiers_legislatifs_and_textes(legislature)
        all_dossiers.update(dossiers)
        all_textes.update(textes)
    return all_dossiers, all_textes


def _get_dossiers_legislatifs_and_textes(
    legislature: int
) -> Tuple[DossierRefsByUID, Dict[str, TexteRef]]:
    # As of June 20th, 2019 the Assemblée Nationale website updated the way
    # their opendata zip content is splitted, without changing old
    # legislatures. Hence we have to keep two ways to parse their content
    # forever. And ever.
    if legislature <= 14:
        data = list(fetch_dossiers_legislatifs_and_textes(legislature).values())[0]
        textes = parse_textes(data["export"]["textesLegislatifs"]["document"])
        dossiers = parse_dossiers(
            data["export"]["dossiersLegislatifs"]["dossier"], textes
        )
    else:
        data = fetch_dossiers_legislatifs_and_textes(legislature)
        textes_data: List[Dict[str, Any]] = [
            dict_["document"]
            for filename, dict_ in data.items()
            if filename.startswith("json/document")
        ]
        textes = parse_textes(textes_data)
        dossiers_data: List[Dict[str, Any]] = [
            dict_
            for filename, dict_ in data.items()
            if filename.startswith("json/dossierParlementaire")
        ]
        dossiers = parse_dossiers(dossiers_data, textes)
    return dossiers, textes


def fetch_dossiers_legislatifs_and_textes(legislature: int) -> dict:
    legislature_roman = roman(legislature)
    url = (
        f"http://data.assemblee-nationale.fr/static/openData/repository/"
        f"{legislature}/loi/dossiers_legislatifs/"
        f"Dossiers_Legislatifs_{legislature_roman}.json.zip"
    )
    return {
        filename: load(json_file)
        for filename, json_file in extract_from_remote_zip(url)
    }


def parse_textes(textes: list) -> Dict[str, TexteRef]:
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
        for item in textes
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


def chambre_texte(item: dict) -> Chambre:
    if item["uid"][4:6] == "AN":
        return Chambre.AN
    if item["uid"][4:6] == "SN":
        return Chambre.SENAT
    raise NotImplementedError


def legislature_texte(item: dict) -> Optional[int]:
    legislature = item["legislature"]
    if not legislature:
        return None
    return int(legislature)


def parse_dossiers(dossiers: list, textes: Dict[str, TexteRef]) -> DossierRefsByUID:
    dossier_dicts = (
        item["dossierParlementaire"] for item in dossiers if isinstance(item, dict)
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
    "AN1": (Chambre.AN, "Première lecture"),
    "SN1": (Chambre.SENAT, "Première lecture"),
    "ANNLEC": (Chambre.AN, "Nouvelle lecture"),
    "SNNLEC": (Chambre.SENAT, "Nouvelle lecture"),
    "ANLDEF": (Chambre.AN, "Lecture définitive"),
}


def parse_dossier(dossier: dict, textes: Dict[str, TexteRef]) -> DossierRef:
    uid = dossier["uid"]
    titre = dossier["titreDossier"]["titre"]
    slug = slugify(dossier["titreDossier"]["titreChemin"] or titre)
    an_url = build_an_url(dossier["titreDossier"]["titreChemin"])
    senat_url = dossier["titreDossier"]["senatChemin"]
    is_plf = "PLF" in dossier
    lectures = [
        lecture
        for acte in top_level_actes(dossier)
        for lecture in gen_lectures(acte, textes, is_plf)
    ]
    return DossierRef(
        uid=uid,
        titre=titre,
        slug=slug,
        an_url=an_url,
        senat_url=senat_url,
        lectures=lectures,
    )


def build_an_url(slug: str) -> str:
    return f"http://www.assemblee-nationale.fr/dyn/15/dossiers/alt/{slug}"


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

        try:
            texte = textes[result.texte_examine]
        except KeyError:
            logger.warning(f"Missing key for texte {result.texte_examine}")
            continue

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
    texte_examine: str
    premiere_lecture: bool


def walk_actes(acte: dict) -> Iterator[WalkResult]:
    texte_depose = None
    texte_commission = None

    def _walk_actes(acte: dict) -> Iterator[WalkResult]:
        nonlocal texte_depose, texte_commission

        code = acte["codeActe"]
        premiere_lecture = code.startswith("AN1") or code.startswith("SN1")
        phase = code.split("-", 1)[1] if "-" in code else ""

        if phase in {"COM-FOND", "COM-AVIS"}:
            texte_examine = texte_depose
        elif phase == "DEBATS":
            texte_examine = texte_commission
            if texte_commission is None:
                logger.warning(
                    "Pas de rapport de la commission saisie au fond, "
                    "examen du texte déposé"
                )
                texte_examine = texte_depose
        else:
            texte_examine = None

        if texte_examine is not None:
            yield WalkResult(
                phase=phase,
                organe=acte["organeRef"],
                texte_examine=texte_examine,
                premiere_lecture=premiere_lecture,
            )

        # Texte déposé
        if phase == "DEPOT":
            texte_depose = acte["texteAssocie"]
            texte_commission = None

        # Texte adopté en commission (ou "null" si aucun amendement n'est adopté)
        if phase == "COM-FOND-RAPPORT":
            if acte["texteAdopte"] is not None:
                texte_commission = acte["texteAdopte"]
            else:
                texte_commission = texte_depose

        for sous_acte in extract_actes(acte):
            yield from _walk_actes(sous_acte)

    yield from _walk_actes(acte)


def extract_actes(acte: dict) -> List[dict]:
    children = (acte.get("actesLegislatifs") or {}).get("acteLegislatif", [])
    if isinstance(children, list):
        return children
    else:
        return [children]
