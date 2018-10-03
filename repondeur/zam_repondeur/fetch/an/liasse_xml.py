import logging
from datetime import date
from functools import partial
from typing import Dict, IO, List, Optional, cast

from lxml import etree

from zam_repondeur.clean import clean_html
from zam_repondeur.data import get_data
from zam_repondeur.fetch.an.dossiers.models import Chambre, Dossier, Texte
from zam_repondeur.fetch.dates import parse_date
from zam_repondeur.fetch.division import _parse_subdiv, SubDiv
from zam_repondeur.models import (
    DBSession,
    Article,
    Amendement,
    Lecture,
    get_one_or_create,
)


logger = logging.getLogger(__name__)


NS = "{http://schemas.assemblee-nationale.fr/referentiel}"


def import_liasse_xml(xml_file: IO[bytes]) -> List[Amendement]:
    try:
        tree = etree.parse(xml_file)
    except etree.XMLSyntaxError:
        message = "Not a valid XML file"
        logger.exception(message)
        raise ValueError(message)
    except Exception:
        message = "Unexpected error while loading XML file"
        logger.exception(message)
        raise ValueError(message)

    root = tree.getroot()
    if root.tag != "amendements":
        message = "Expecting 'amendements' as a root element"
        logger.error(message)
        raise ValueError(message)

    uid_map: Dict[str, Amendement] = {}
    for child in root:
        uid = child.find(f"./{NS}uid").text
        amendement = _make_amendement(child, uid_map)
        uid_map[uid] = amendement
    return list(uid_map.values())


def _make_amendement(node: etree.Element, uid_map: Dict[str, Amendement]) -> Amendement:
    extract = partial(extract_from_node, node)

    subdiv = _parse_division(node)

    texte_uid = extract("identifiant", "saisine", "refTexteLegislatif")
    if texte_uid is None:
        raise ValueError("Missing refTexteLegislatif")

    is_gouvernemental = extract("signataires", "auteur", "typeAuteur") == "Gouvernement"

    if is_gouvernemental:
        auteur_name = "LE GOUVERNEMENT"
        groupe_name = None
        matricule = None
    else:
        auteur_uid = extract("signataires", "auteur", "acteurRef")
        if auteur_uid is None:
            raise ValueError("Missing auteur acteurRef")
        auteur_name = get_auteur_name(auteur_uid)
        matricule = auteur_uid

        groupe_uid = extract("signataires", "auteur", "groupePolitiqueRef")
        if groupe_uid is None:
            raise ValueError("Missing auteur groupePolitiqueRef")
        groupe_name = get_groupe_name(groupe_uid)

    lecture, created = get_one_or_create(
        DBSession,
        Lecture,
        chambre=Chambre.AN.value,
        session=extract("identifiant", "legislature"),
        num_texte=get_texte_number(texte_uid),
        organe=extract("identifiant", "saisine", "organeExamen"),
    )
    article, created = get_one_or_create(
        DBSession,
        Article,
        lecture=lecture,
        type=subdiv.type_,
        num=subdiv.num,
        mult=subdiv.mult,
        pos=subdiv.pos,
    )
    amendement, created = get_one_or_create(
        DBSession,
        Amendement,
        lecture=lecture,
        num=to_int(extract("identifiant", "numero")),
    )
    amendement.article = article
    amendement.alinea = to_int(extract("pointeurFragmentTexte", "alinea", "numero"))
    amendement.auteur = auteur_name
    amendement.matricule = matricule
    amendement.groupe = groupe_name
    amendement.date_depot = to_date(extract("dateDepot"))
    amendement.sort = get_sort(
        sort=extract("sort", "sortEnSeance"), etat=extract("etat")
    )
    amendement.dispositif = clean_html(extract("corps", "dispositif") or "")
    amendement.objet = clean_html(extract("corps", "exposeSommaire") or "")
    amendement.parent = get_parent(extract("amendementParent"), uid_map)
    return cast(Amendement, amendement)


def _parse_division(node: etree.Element) -> SubDiv:
    extract = partial(extract_from_node, node)

    division_type = extract("pointeurFragmentTexte", "division", "type")
    if division_type is None:
        raise ValueError("Missing division type")

    if division_type == "TITRE":
        return SubDiv(type_="titre", num="", mult="", pos="")

    division_titre = extract("pointeurFragmentTexte", "division", "titre")
    if division_titre is None:
        raise ValueError("Missing division titre")

    return _parse_subdiv(division_titre)


def extract_from_node(node: etree.Element, *path: str) -> Optional[str]:
    element_path = "." + "/".join((NS + elem) for elem in path)
    elem: Optional[etree.Element] = node.find(element_path)
    if elem is None:
        return None
    text: str = elem.text
    return text


def to_int(text: Optional[str]) -> Optional[int]:
    if text is None:
        return None
    return int(text)


def to_date(text: Optional[str]) -> Optional[date]:
    if text is None:
        return None
    return parse_date(text)


def get_texte_number(uid: str) -> int:
    texte = _find_texte(uid)
    numero: int = texte.numero
    return numero


def _find_texte(uid: str) -> Texte:
    # FIXME: this is not efficient
    dossiers: Dict[str, Dossier] = get_data("dossiers")
    for dossier in dossiers.values():
        for lecture in dossier.lectures:
            if lecture.texte.uid == uid:
                return lecture.texte
    raise ValueError(f"Unknown texte {uid}")


def get_sort(sort: Optional[str], etat: Optional[str]) -> str:
    if sort is not None:
        return sort
    if etat is not None and etat not in ("En traitement", "A discuter"):
        return etat
    return ""


def get_auteur_name(uid: str) -> str:
    acteurs = get_data("acteurs")
    if uid not in acteurs:
        raise ValueError(f"Unknown auteur {uid}")
    acteur = acteurs[uid]
    ident: Dict[str, str] = acteur["etatCivil"]["ident"]
    return ident["prenom"] + " " + ident["nom"]


def get_groupe_name(uid: str) -> str:
    organes = get_data("organes")
    if uid not in organes:
        raise ValueError(f"Unknown groupe {uid}")
    libelle: str = organes[uid]["libelle"]
    return libelle


def get_parent(
    uid: Optional[str], uid_map: Dict[str, Amendement]
) -> Optional[Amendement]:
    if uid is None:
        return None
    try:
        return uid_map[uid]
    except KeyError:
        raise ValueError(f"Unknown parent amendement {uid}")
