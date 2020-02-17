import logging
import re
from datetime import date
from functools import partial
from typing import IO, Dict, List, Optional, Tuple, cast

from defusedxml.lxml import RestrictedElement, parse
from lxml.etree import XMLSyntaxError  # nosec

from zam_repondeur.models import (
    Amendement,
    Article,
    Chambre,
    DBSession,
    Lecture,
    get_one_or_create,
)
from zam_repondeur.models.division import SubDiv
from zam_repondeur.services.clean import clean_html
from zam_repondeur.services.data import repository
from zam_repondeur.services.dossiers import (
    get_dossiers_legislatifs_open_data_from_cache,
)
from zam_repondeur.services.fetch.an.division import parse_avant_apres
from zam_repondeur.services.fetch.an.dossiers.models import (
    DossierRef,
    LectureRef,
    TexteRef,
)
from zam_repondeur.services.fetch.dates import parse_date
from zam_repondeur.services.fetch.division import parse_subdiv

logger = logging.getLogger(__name__)


NS = "{http://schemas.assemblee-nationale.fr/referentiel}"


class BadChambre(Exception):
    """
    Liasse import is only for Assemblée nationale
    """


class LectureDoesNotMatch(Exception):
    """
    The liasse contains amendements for another lecture
    """

    def __init__(self, lecture_fmt: str) -> None:
        self.lecture_fmt = lecture_fmt


def import_liasse_xml(
    xml_file: IO[bytes], lecture: Lecture
) -> Tuple[List[Amendement], List[Tuple[str, str]]]:

    if lecture.chambre != Chambre.AN:
        raise BadChambre

    try:
        tree = parse(xml_file)
    except XMLSyntaxError:
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
    errors = []
    for child in root:
        if extract_from_node(child, "etat") == "A déposer":
            num_long = extract_from_node(child, "numeroLong")
            logger.warning(f"Ignoring amendement {num_long} (à déposer)")
            continue

        uid = child.find(f"./{NS}uid").text
        try:
            amendement = _make_amendement(child, uid_map, lecture)
            uid_map[uid] = amendement
        except LectureDoesNotMatch:
            raise
        except Exception as exc:
            logger.exception(f"Failed to import amendement {uid} from liasse")
            errors.append((uid, str(exc)))

    return list(uid_map.values()), errors


def _make_amendement(
    node: RestrictedElement, uid_map: Dict[str, Amendement], lecture: Lecture
) -> Amendement:
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

    check_same_lecture(
        lecture=lecture,
        texte_uid=texte_uid,
        partie=extract_partie(node),
        organe=extract("identifiant", "saisine", "organeExamen"),
    )

    article, created = get_one_or_create(
        Article,
        lecture=lecture,
        type=subdiv.type_,
        num=subdiv.num,
        mult=subdiv.mult,
        pos=subdiv.pos,
    )
    parent = get_parent(extract("amendementParent"), uid_map, lecture)
    amendement, created = get_one_or_create(
        Amendement,
        create_kwargs={"article": article, "parent": parent},
        lecture=lecture,
        num=to_int(extract("identifiant", "numero")),
    )
    if not created:
        amendement.article = article
        amendement.parent = parent
    amendement.alinea = to_int(extract("pointeurFragmentTexte", "alinea", "numero"))
    amendement.auteur = auteur_name
    amendement.matricule = matricule
    amendement.groupe = groupe_name
    amendement.date_depot = to_date(extract("dateDepot"))
    amendement.sort = get_sort(
        sort=extract("sort", "sortEnSeance"), etat=extract("etat")
    )
    amendement.corps = clean_html(extract("corps", "dispositif") or "")
    amendement.expose = clean_html(extract("corps", "exposeSommaire") or "")
    return cast(Amendement, amendement)


def check_same_lecture(
    lecture: Lecture, texte_uid: str, partie: Optional[int], organe: Optional[str]
) -> None:
    if organe is None:
        raise ValueError("Missing organeExamen")

    texte_ref = repository.get_opendata_texte(texte_uid)
    if texte_ref is None:
        raise ValueError("Unknown texte")

    if (
        texte_ref.chambre != lecture.texte.chambre
        or texte_ref.legislature != lecture.texte.legislature
        or texte_ref.numero != lecture.texte.numero
        or partie != lecture.partie
        or organe != lecture.organe
    ):
        dossier_ref, lecture_ref = _find_dossier_lecture(texte_ref)
        lecture_fmt = f"{lecture_ref.label} ({dossier_ref.titre})"
        raise LectureDoesNotMatch(lecture_fmt)


def _parse_division(node: RestrictedElement) -> SubDiv:
    extract = partial(extract_from_node, node)

    division_titre = extract("pointeurFragmentTexte", "division", "titre")

    division_type = extract("pointeurFragmentTexte", "division", "type")
    if division_type is None:
        raise ValueError("Missing division type")

    pos = parse_avant_apres(
        extract("pointeurFragmentTexte", "division", "avant_A_Apres") or ""
    )
    if division_type == "TITRE":
        return SubDiv(type_="titre", num="", mult="", pos=pos)

    if division_type == "CHAPITRE":
        division_rattachee = extract(
            "pointeurFragmentTexte", "division", "divisionRattachee"
        )
        if division_rattachee:
            return parse_subdiv(division_rattachee)
        else:
            mo = re.match(r"^([A-Za-z0-9])+", division_titre or "")
            num = mo.group(1) if mo is not None else ""
            return SubDiv(type_="chapitre", num=num, mult="", pos=pos)

    if division_titre is None:
        raise ValueError("Missing division titre")

    subdiv = parse_subdiv(division_titre)
    return subdiv._replace(pos=pos)


def extract_from_node(node: RestrictedElement, *path: str) -> Optional[str]:
    element_path = "." + "/".join((NS + elem) for elem in path)
    elem: Optional[RestrictedElement] = node.find(element_path)
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


def _find_dossier_lecture(texte_ref: TexteRef) -> Tuple[DossierRef, LectureRef]:
    # FIXME: this is not efficient
    for dossier_ref in get_dossiers_legislatifs_open_data_from_cache().values():
        for lecture_ref in dossier_ref.lectures:
            if lecture_ref.texte == texte_ref:
                return dossier_ref, lecture_ref
    raise ValueError(f"Unknown texte {texte_ref}")


def extract_partie(node: RestrictedElement) -> Optional[int]:
    text = extract_from_node(node, "identifiant", "saisine", "numeroPartiePLF")
    if text is not None and text != "0":
        return int(text)
    return None


def get_sort(sort: Optional[str], etat: Optional[str]) -> str:
    if sort is not None:
        return sort
    if etat is not None and etat not in ("En traitement", "A discuter"):
        return etat
    return ""


def get_auteur_name(uid: str) -> str:
    acteur = repository.get_opendata_acteur(uid)
    if acteur is None:
        raise ValueError(f"Unknown auteur {uid}")
    ident: Dict[str, str] = acteur["etatCivil"]["ident"]
    return ident["prenom"] + " " + ident["nom"]


def get_groupe_name(uid: str) -> str:
    groupe = repository.get_opendata_organe(uid)
    if groupe is None:
        raise ValueError(f"Unknown groupe {uid}")
    libelle: str = groupe["libelle"]
    return libelle


def get_parent(
    uid: Optional[str], uid_map: Dict[str, Amendement], lecture: Lecture
) -> Optional[Amendement]:
    if uid is None:
        return None
    try:
        return uid_map[uid]
    except KeyError:
        num = get_number_from_uid(uid)
        parent: Optional[Amendement] = (
            DBSession.query(Amendement)
            .filter(Amendement.lecture == lecture, Amendement.num == num)
            .first()
        )
        if parent is None:
            raise ValueError(f"Unknown parent amendement {num}") from None
        return parent


def get_number_from_uid(uid: str) -> int:
    """
    Get the amendement number from the UID

    UIDs are supposed to be opaque, but if the parent amendement is not included
    then we have to extract the number anyway :-/
    """
    mo = re.match(r"^AM.+N(?P<num>\d+)$", uid)
    if mo is None:
        raise ValueError(f"Cannot extract amendement number from {uid}") from None
    return int(mo.group("num"))
