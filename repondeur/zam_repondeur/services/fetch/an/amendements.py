import logging
import re
from collections import OrderedDict
from http import HTTPStatus
from typing import Dict, List, NamedTuple, Optional, Set, Tuple
from urllib.parse import urljoin

import xmltodict
from requests.exceptions import ConnectionError

from zam_repondeur.models import (
    Amendement,
    Article,
    DBSession,
    Lecture,
    get_one_or_create,
)
from zam_repondeur.models.division import SubDiv
from zam_repondeur.models.events.amendement import BatchUnset
from zam_repondeur.services.fetch.amendements import FetchResult, RemoteSource
from zam_repondeur.services.fetch.division import parse_subdiv
from zam_repondeur.services.fetch.exceptions import FetchError, NotFound
from zam_repondeur.services.fetch.http import get_http_session
from zam_repondeur.templating import render_template
from zam_repondeur.utils import Timer

from ..missions import MissionRef
from .division import parse_avant_apres

logger = logging.getLogger(__name__)


BASE_URL = "http://www.assemblee-nationale.fr"

# Deprecation warning: this API for fetching amendements will be removed in the future
# and has no Service Level Agreement (SLA)
PATTERN_LISTE = (
    "/eloi/{legislature}/amendements/{texte}{suffixe}/{organe_abrev}/liste.xml"
)
PATTERN_AMENDEMENT = (
    "/dyn/{legislature}/amendements/"
    "{texte}{suffixe}/{organe_abrev}/{numero_prefixe}.xml"
)
PATTERN_AMENDEMENT_FALLBACK = (
    "/{legislature}/xml/amendements/"
    "{texte}{suffixe}/{organe_abrev}/{numero_prefixe}.xml"
)

# When trying to discover amendements published but not yet included in the list,
# we can't try all possible numbers, so we'll stop after a string of 404s
MAX_404 = 30


class OrganeNotFound(Exception):
    def __init__(self, organe: str) -> None:
        super().__init__(f"Organe {organe} not found in data")
        self.organe = organe


class AssembleeNationale(RemoteSource):
    def prepare(self, lecture: Lecture) -> None:
        if self.prefetching_enabled:
            logger.info("Préchargement des amendements de %r", lecture)
            with Timer() as timer:
                self._fetch(lecture, dry_run=True)
            logger.info("Temps de préchargement : %.1fs", timer.elapsed())

    def fetch(self, lecture: Lecture) -> FetchResult:
        logger.info("Récupération des amendements de %r", lecture)
        with Timer() as timer:
            res = self._fetch(lecture)
        logger.info("Temps de récupération : %.1fs", timer.elapsed())
        return res

    def _fetch(self, lecture: Lecture, dry_run: bool = False) -> FetchResult:
        result = FetchResult([], 0, [])

        try:
            discussion_items = fetch_discussion_list(lecture)
        except NotFound:
            return FetchResult([], 0, [])

        if not discussion_items:
            logger.warning("Could not find amendements from %r", lecture)

        if not dry_run:
            reset_amendements_positions(lecture, discussion_items)

        result += self._fetch_amendements_discussed(
            lecture, discussion_items, dry_run=dry_run
        )
        lecture.reset_fetch_progress()

        if not dry_run:
            result += self._fetch_amendements_other(
                lecture=lecture,
                discussion_nums={
                    parse_num_in_liste(d["@numero"])[1] for d in discussion_items
                },
                prefix=find_prefix(discussion_items, lecture),
            )

        return result

    def _fetch_amendements_discussed(
        self,
        lecture: Lecture,
        discussion_items: List[OrderedDict],
        dry_run: bool = False,
    ) -> FetchResult:
        amendements: List[Amendement] = []
        created = 0
        errored: List[str] = []
        total = len(discussion_items)

        for position, item in enumerate(discussion_items, start=1):
            numero_prefixe = item["@numero"]
            id_discussion_commune = (
                int(item["@discussionCommune"]) if item["@discussionCommune"] else None
            )
            id_identique = (
                int(item["@discussionIdentique"])
                if item["@discussionIdentique"]
                else None
            )
            try:
                amendement, created_ = self.fetch_amendement(
                    lecture=lecture,
                    numero_prefixe=numero_prefixe,
                    position=position,
                    id_discussion_commune=id_discussion_commune,
                    id_identique=id_identique,
                    dry_run=dry_run,
                )
            except NotFound:
                prefix, num = parse_num_in_liste(numero_prefixe)
                logger.warning("Could not find amendement %r for %r", num, lecture)
                errored.append(str(num))
                continue
            except Exception:
                prefix, num = parse_num_in_liste(numero_prefixe)
                logger.exception(
                    "Error while fetching amendement %r for %r", num, lecture
                )
                errored.append(str(num))
                continue
            amendements.append(amendement)
            self._set_fetch_progress(lecture, position, total, dry_run)
            created += int(created_)
        return FetchResult(amendements, created, errored)

    def _set_fetch_progress(
        self, lecture: Lecture, position: int, total: int, dry_run: bool
    ) -> None:
        current = position if dry_run else total + position
        # Dry run + real run + _fetch_amendements_other
        total = total + total + MAX_404
        lecture.set_fetch_progress(current, total)

    def _fetch_amendements_other(
        self, lecture: Lecture, discussion_nums: Set[int], prefix: str
    ) -> FetchResult:
        amendements: List[Amendement] = []
        created = 0
        errored: List[str] = []

        max_num_in_liste = max(discussion_nums, default=0)
        max_num_in_lecture = max((amdt.num for amdt in lecture.amendements), default=0)
        max_num_seen = max(max_num_in_liste, max_num_in_lecture)

        numero = 0

        while numero < (max_num_seen + MAX_404):
            numero += 1
            if numero in discussion_nums:
                continue
            try:
                amendement, created_ = self.fetch_amendement(
                    lecture=lecture,
                    numero_prefixe=f"{prefix}{numero}",
                    position=None,
                    id_discussion_commune=None,
                    id_identique=None,
                )
            except NotFound:
                continue
            except Exception:
                logger.exception("Error while fetching amendement %r", numero)
                errored.append(str(numero))
                continue
            amendements.append(amendement)
            created += int(created_)
            if numero > max_num_seen:
                max_num_seen = numero
        return FetchResult(amendements, created, errored)

    def fetch_amendement(
        self,
        lecture: Lecture,
        numero_prefixe: str,
        position: Optional[int],
        id_discussion_commune: Optional[int] = None,
        id_identique: Optional[int] = None,
        dry_run: bool = False,
    ) -> Tuple[Amendement, bool]:
        """
        Récupère un amendement depuis son numéro.
        """
        logger.info("Récupération de l'amendement %r", numero_prefixe)
        amend = _retrieve_amendement(lecture, numero_prefixe)
        if dry_run:
            return Amendement(), False  # Dummy.

        article = _get_article(lecture, amend["division"])
        parent = _get_parent(lecture, article, amend)
        amendement, created = self._create_or_update_amendement(
            lecture,
            article,
            parent,
            amend,
            position,
            id_discussion_commune,
            id_identique,
        )
        return amendement, created

    def _create_or_update_amendement(
        self,
        lecture: Lecture,
        article: Article,
        parent: Optional[Amendement],
        amend: OrderedDict,
        position: Optional[int],
        id_discussion_commune: Optional[int],
        id_identique: Optional[int],
    ) -> Tuple[Amendement, bool]:
        amendement, created = get_one_or_create(
            Amendement,
            create_kwargs={"article": article, "parent": parent},
            lecture=lecture,
            num=int(amend["numero"]),
        )

        if (
            not created
            and amendement.location.batch
            and amendement.article.pk != article.pk
        ):
            BatchUnset.create(amendement=amendement, request=None)

        raw_auteur = amend.get("auteur")
        if not raw_auteur:
            logger.warning("Unknown auteur for amendement %s", amend["numero"])
            matricule, groupe, auteur = "", "Non trouvé", "Non trouvé"
        else:
            matricule = raw_auteur["tribunId"]
            groupe = get_groupe(raw_auteur, amendement.num)
            auteur = get_auteur(raw_auteur)

        mission_ref = get_mission_ref(amend)
        modified = False
        modified |= self.update_rectif(amendement, get_rectif(amend))
        modified |= self.update_corps(amendement, get_corps(amend))
        modified |= self.update_expose(
            amendement, unjustify(get_str_or_none(amend, "exposeSommaire") or "")
        )
        modified |= self.update_sort(amendement, get_sort(amend))
        modified |= self.update_attributes(
            amendement,
            article=article,
            parent=parent,
            position=position,
            id_discussion_commune=id_discussion_commune,
            id_identique=id_identique,
            matricule=matricule,
            groupe=groupe,
            auteur=auteur,
            mission_titre=mission_ref.titre if mission_ref else None,
            mission_titre_court=mission_ref.titre_court if mission_ref else None,
        )

        DBSession.flush()  # make sure foreign keys are updated

        return amendement, created


def reset_amendements_positions(
    lecture: Lecture, discussion_items: List[OrderedDict]
) -> None:

    current_order = {
        amdt.num: amdt.position
        for amdt in lecture.amendements
        if amdt.position is not None
    }

    new_order = {
        parse_num_in_liste(item["@numero"])[1]: index
        for index, item in enumerate(discussion_items, start=1)
    }

    # Reset position for all amendements that moved,
    # so that we don't break the UNIQUE INDEX constraint later
    for amdt in lecture.amendements:
        if amdt.num not in current_order:
            continue
        if new_order.get(amdt.num) != current_order[amdt.num]:
            amdt.position = None
        if amdt.num not in new_order:  # removed
            logger.info("Amendement %s retiré de la discussion", amdt.num)
    DBSession.flush()


def find_prefix(discussion_items: List[OrderedDict], lecture: Lecture) -> str:
    if discussion_items:
        numero_prefixe = discussion_items[0]["@numero"]
        prefix, _ = parse_num_in_liste(numero_prefixe)
        return prefix
    return get_organe_prefix(lecture.organe)


def get_organe_prefix(organe: str) -> str:
    abrev = get_organe_abrev(organe)
    return _ORGANE_PREFIX.get(abrev, "")


_ORGANE_PREFIX = {
    "CION_FIN": "CF",  # Finances
    "CION-SOC": "AS",  # Affaires sociales
    "CION-CEDU": "AC",  # Affaires culturelles et éducation
    "CION-ECO": "CE",  # Affaires économiques
    "CION_AFETR": "AE",  # Affaires étrangères
    "CION_DEF": "DN",  # Défense
    "CION_LOIS": "CL",  # Lois
    "CION-DVP": "CD",  # Développement durable
}


def _retrieve_content(
    url: str, force_list: Optional[Tuple[str]] = None
) -> Dict[str, OrderedDict]:
    logger.info("Récupération de %r", url)
    http_session = get_http_session()
    try:
        resp = http_session.get(url)
    except ConnectionError:
        raise NotFound(url)

    if resp.status_code == HTTPStatus.NOT_FOUND:
        raise NotFound(url)

    # Due to a configuration change on the AN web server, we now get a 500 error
    # for abandoned or non-existing amendements, so we'll consider this a 404 too :(
    if resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        raise NotFound(url)

    # Sometimes the URL returns a 200 but the content is empty which leads to
    # a parsing error from xmltodict if not handled manually before.
    if not resp.content:
        raise NotFound(url)

    # Other errors
    if resp.status_code >= 400:
        raise FetchError(url, resp)

    result: OrderedDict = xmltodict.parse(resp.content, force_list=force_list)
    return result


_FORCE_LIST_KEYS_LISTE = ("amendement",)


def fetch_discussion_list(lecture: Lecture) -> List[OrderedDict]:
    """
    Récupère la liste ordonnée des amendements soumis à la discussion.

    Les amendements irrecevables ou encore en traitement ne sont pas inclus.
    """
    url = build_url(lecture)
    content = _retrieve_content(url, force_list=_FORCE_LIST_KEYS_LISTE)

    try:
        discussed_amendements: List[OrderedDict] = (
            content["amdtsParOrdreDeDiscussion"]["amendements"]["amendement"]
        )
    except TypeError:
        return []

    return discussed_amendements


_FORCE_LIST_KEYS_AMENDEMENT = ("programmeAmdt",)


def _retrieve_amendement(lecture: Lecture, numero_prefixe: str) -> OrderedDict:
    url = build_url(lecture, numero_prefixe)
    try:
        content = _retrieve_content(url, force_list=_FORCE_LIST_KEYS_AMENDEMENT)
    except NotFound:
        url = build_url(lecture, numero_prefixe, fallback=True)
        content = _retrieve_content(url)
    return content["amendement"]


def _get_article(lecture: Lecture, division: dict) -> Article:
    subdiv = parse_division(division)
    article: Article
    created: bool
    article, created = get_one_or_create(
        Article,
        lecture=lecture,
        type=subdiv.type_,
        num=subdiv.num,
        mult=subdiv.mult,
        pos=subdiv.pos,
    )
    return article


def _get_parent(
    lecture: Lecture, article: Article, amend: OrderedDict
) -> Optional[Amendement]:
    parent_num, parent_rectif = Amendement.parse_num(get_parent_raw_num(amend))
    parent: Optional[Amendement]
    if parent_num:
        parent, created = get_one_or_create(
            Amendement,
            create_kwargs={"article": article, "rectif": parent_rectif},
            lecture=lecture,
            num=parent_num,
        )
    else:
        parent = None
    return parent


def build_url(
    lecture: Lecture, numero_prefixe: str = "", fallback: bool = False
) -> str:

    legislature = lecture.texte.legislature
    texte = f"{lecture.texte.numero:04}"

    # The 1st "lecture" of the "projet de loi de finances" (PLF) has two parts
    if lecture.partie == 1:
        suffixe = "A"
    elif lecture.partie == 2:
        suffixe = "C"
    else:
        suffixe = ""

    organe_abrev = get_organe_abrev(lecture.organe)

    if numero_prefixe:
        pattern = PATTERN_AMENDEMENT_FALLBACK if fallback else PATTERN_AMENDEMENT
    else:
        pattern = PATTERN_LISTE

    path = pattern.format(
        legislature=legislature,
        texte=texte,
        suffixe=suffixe,
        organe_abrev=organe_abrev,
        numero_prefixe=numero_prefixe,
    )
    url: str = urljoin(BASE_URL, path)
    return url


def get_organe_abrev(organe_uid: str) -> str:
    from zam_repondeur.services.data import repository

    organe = repository.get_opendata_organe(organe_uid)
    if organe is None:
        raise OrganeNotFound(organe)
    abrev: str = organe["libelleAbrev"]
    return abrev


def parse_num_in_liste(num_long: str) -> Tuple[str, int]:
    mo = _RE_NUM.match(num_long)
    if mo is None:
        raise ValueError(f"Cannot parse amendement number {num_long!r}")
    return mo.group("acronyme"), int(mo.group("num"))


_RE_NUM = re.compile(r"(?P<acronyme>[A-Z]*)(?P<num>\d+)")


def get_auteur(raw_auteur: OrderedDict) -> str:
    if int(raw_auteur["estGouvernement"]):
        return "LE GOUVERNEMENT"
    return f"{raw_auteur['nom']} {raw_auteur['prenom']}"


def get_groupe(raw_auteur: OrderedDict, amendement_num: int) -> str:
    from zam_repondeur.services.data import repository

    gouvernemental = bool(int(raw_auteur["estGouvernement"]))
    rapporteur = bool(int(raw_auteur["estRapporteur"]))
    if gouvernemental or rapporteur:
        return ""

    groupe_tribun_id = get_str_or_none(raw_auteur, "groupeTribunId")
    if groupe_tribun_id is None:
        logger.warning("Missing groupeTribunId value for amendement %s", amendement_num)
        return "Non précisé"

    groupe = repository.get_opendata_organe(f"PO{groupe_tribun_id}")
    if groupe is None:
        logger.warning(
            "Unknown groupe tribun 'PO%s' in groupes for amendement %s",
            groupe_tribun_id,
            amendement_num,
        )
        return "Non trouvé"

    libelle: str = groupe["libelle"]
    return libelle


ETATS_OK = {
    "AT",  # à traiter
    "T",  # traité
    "ER",  # en recevabilité
    "R",  # recevable
    "AC",  # à discuter
    "DI",  # discuté
}


def get_sort(amendement: OrderedDict) -> str:
    sort = get_str_or_none(amendement, "sortEnSeance")
    if sort is not None:
        return sort.lower()
    if (
        amendement["retireAvantPublication"] == "1"
        or amendement.get("retireApresPublication", "0") == "1"
    ):
        return "Retiré"
    etat = get_str_or_none(amendement, "etat")
    if etat not in ETATS_OK:
        return "Irrecevable"
    return ""


def get_parent_raw_num(amendement: OrderedDict) -> str:
    return get_str_or_none(amendement, "numeroParent") or ""


def get_rectif(amendement: OrderedDict) -> int:
    numero_long = get_str_or_none(amendement, "numeroLong")
    if numero_long is None:
        return 0
    return parse_numero_long_with_rect(numero_long)


def get_corps(amendement: OrderedDict) -> str:
    if "listeProgrammesAmdt" in amendement:
        return render_credits_tables(amendement)
    else:
        return unjustify(get_str_or_none(amendement, "dispositif") or "")


def render_credits_tables(amendement: OrderedDict) -> str:
    ae = _extract_credits_table(amendement, type_credits="aE")
    cp = _extract_credits_table(amendement, type_credits="cP")
    return render_template(
        "mission_table.html",
        context={
            "ae": ae,
            "cp": cp,
            "cp_only": all((p.pos, p.neg) == ("0", "0") for p in ae.programmes),
            "ae_only": all((p.pos, p.neg) == ("0", "0") for p in cp.programmes),
            "ae_cp_different": ae != cp,
        },
    )


class LigneCredits(NamedTuple):
    libelle: str
    pos: str
    neg: str


class TableauCredits(NamedTuple):
    programmes: List[LigneCredits]
    totaux: LigneCredits
    solde: str


def _extract_credits_table(
    amendement: OrderedDict, type_credits: str
) -> TableauCredits:
    programmes = amendement["listeProgrammesAmdt"]["programmeAmdt"]

    new_format = "aEPositifFormat" in programmes[0]
    if new_format:
        pos_key, neg_key = "Positif", "Negatif"
    else:
        pos_key, neg_key = "SupplementairesOuvertes", "Annulees"

    return TableauCredits(
        programmes=[
            LigneCredits(
                libelle=_extract_libelle(programme),
                pos=programme[type_credits + pos_key + "Format"],
                neg=programme[type_credits + neg_key + "Format"],
            )
            for programme in programmes
        ],
        totaux=LigneCredits(
            libelle="Totaux",
            pos=amendement["total" + type_credits.upper() + pos_key + "Format"],
            neg=amendement["total" + type_credits.upper() + neg_key + "Format"],
        ),
        solde=amendement["solde" + type_credits.upper() + "Format"],
    )


def _extract_libelle(programme: OrderedDict) -> str:
    libelle: str = programme["libelleProgrammeAmdt"]
    if programme["programmeAmdtNouveau"] == "true":
        libelle += " (ligne nouvelle)"
    return libelle


def get_mission_ref(amendement: OrderedDict) -> Optional[MissionRef]:
    if "missionVisee" not in amendement:
        return None
    mission_visee = get_str_or_none(amendement, "missionVisee")
    if mission_visee is None:
        return None
    return parse_mission_visee(mission_visee)


RE_NUM_LONG = re.compile(
    r"""
    (?P<prefix>[A-Z]*)
    (?P<num>\d+)
    (?P<rect>\s\((?:(?P<rect_mult>\d+)\w+\s)?Rect\))?
    """,
    re.VERBOSE,
)


def parse_numero_long_with_rect(text: str) -> int:
    mo = RE_NUM_LONG.match(text)
    if mo is not None and mo.group("rect"):
        return int(mo.group("rect_mult") or 1)
    return 0


RE_MISSION_VISEE = re.compile(r"""(Mission )?« (?P<titre_court>.*) »""")


def parse_mission_visee(mission_visee: str) -> MissionRef:
    mo = RE_MISSION_VISEE.match(mission_visee)
    titre_court = mo.group("titre_court") if mo is not None else mission_visee
    return MissionRef(titre=mission_visee, titre_court=titre_court)


def get_str_or_none(amendement: OrderedDict, key: str) -> Optional[str]:
    value = amendement[key]
    if isinstance(value, str):
        return value
    if isinstance(value, OrderedDict) and value.get("@xsi:nil") == "true":
        return None
    raise ValueError(f"Unexpected value {value!r} for key {key!r}")


def unjustify(content: str) -> str:
    return content.replace(' style="text-align: justify;"', "")


def parse_division(division: dict) -> SubDiv:
    if division["type"] == "TITRE":
        return SubDiv("titre", "", "", "")
    if division["type"] == "ARTICLE":
        subdiv = parse_subdiv(division["titre"])
    else:
        subdiv = parse_subdiv(division["divisionRattache"])
    if division["avantApres"]:
        pos = parse_avant_apres(division["avantApres"])
        subdiv = subdiv._replace(pos=pos)
    return subdiv
