import logging
import re
from abc import ABC, abstractmethod
from collections import OrderedDict
from http import HTTPStatus
from typing import Any, Dict, List, NamedTuple, Optional, Set, Tuple
from urllib.parse import urljoin

import xmltodict
from requests.exceptions import ConnectionError
from sqlalchemy.orm.exc import NoResultFound

from zam_repondeur.decorator import reify
from zam_repondeur.models import (
    Amendement,
    Article,
    DBSession,
    Lecture,
    get_one_or_create,
)
from zam_repondeur.models.division import SubDiv
from zam_repondeur.models.events.amendement import BatchUnset
from zam_repondeur.services.fetch.amendements import FetchResult, RemoteSource, Source
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


class CollectedChanges(NamedTuple):
    """
    Changes found by the collect phase
    """

    list_fetch_success: bool
    position_changes: Dict[int, Optional[int]]
    actions: List["Action"]
    errored: List[str]

    @classmethod
    def create(
        cls,
        list_fetch_success: bool = True,
        position_changes: Optional[Dict[int, Optional[int]]] = None,
        actions: Optional[List["Action"]] = None,
        errored: Optional[List[str]] = None,
    ) -> "CollectedChanges":
        if position_changes is None:
            position_changes = {}
        if actions is None:
            actions = []
        if errored is None:
            errored = []
        return cls(list_fetch_success, position_changes, actions, errored)


class AssembleeNationale(RemoteSource):
    def fetch(self, lecture: Lecture) -> FetchResult:
        logger.info("Récupération des amendements de %r", lecture)

        try:
            with Timer() as collect_timer:
                changes = self._collect(lecture)
            logger.info("Time to collect: %.1fs", collect_timer.elapsed())

            with Timer() as apply_timer:
                res = self._apply(lecture, changes)
            logger.info("Time to apply: %.1fs", apply_timer.elapsed())

            logger.info(
                "Total time: %.1fs", collect_timer.elapsed() + apply_timer.elapsed()
            )
            return res
        finally:
            lecture.reset_fetch_progress()

    def fetch_amendement(
        self, lecture: Lecture, numero_prefixe: str, position: Optional[int]
    ) -> Tuple[Optional[Amendement], bool]:
        amendement, action = self._collect_amendement(lecture, numero_prefixe, position)
        created = isinstance(action, CreateAmendement)
        if action is not None:
            result = action.apply(lecture)
            DBSession.flush()
            amendement = result.amendements[0]
        return amendement, created

    def _collect(self, lecture: Lecture) -> CollectedChanges:
        try:
            derouleur = fetch_discussion_list(lecture)
        except NotFound:
            return CollectedChanges.create(list_fetch_success=False)

        if not derouleur.discussion_items:
            logger.warning("Could not find amendements from %r", lecture)

        position_changes = derouleur.updated_amendement_positions()

        actions, errored = self._collect_amendements_discussed(lecture, derouleur)

        other_actions, other_failed_nums = self._collect_amendements_other(
            lecture=lecture,
            discussion_nums=derouleur.discussion_nums,
            prefix=derouleur.find_prefix(),
        )

        return CollectedChanges.create(
            position_changes=position_changes,
            actions=actions + other_actions,
            errored=errored + other_failed_nums,
        )

    def _collect_amendements_discussed(
        self, lecture: Lecture, derouleur: "ANDerouleurData"
    ) -> Tuple[List["Action"], List[str]]:
        actions: List["Action"] = []
        errored: List[str] = []

        total = len(derouleur.discussion_items)

        for position, item in enumerate(derouleur.discussion_items, start=1):
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
                amendement, action = self._collect_amendement(
                    lecture=lecture,
                    numero_prefixe=numero_prefixe,
                    position=position,
                    id_discussion_commune=id_discussion_commune,
                    id_identique=id_identique,
                )
                if action is not None:
                    actions.append(action)
            except NotFound:
                prefix, num = ANDerouleurData.parse_num_in_liste(numero_prefixe)
                logger.warning("Could not find amendement %r for %r", num, lecture)
                errored.append(str(num))
                continue
            except Exception:
                prefix, num = ANDerouleurData.parse_num_in_liste(numero_prefixe)
                logger.exception(
                    "Error while fetching amendement %r for %r", num, lecture
                )
                errored.append(str(num))
                continue
            self._set_fetch_progress(lecture, position, total)
        return actions, errored

    def _collect_amendements_other(
        self, lecture: Lecture, discussion_nums: Set[int], prefix: str
    ) -> Tuple[List["Action"], List[str]]:
        actions: List["Action"] = []
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
                amendement, action = self._collect_amendement(
                    lecture=lecture,
                    numero_prefixe=f"{prefix}{numero}",
                    position=None,
                    id_discussion_commune=None,
                    id_identique=None,
                )
                if action is not None:
                    actions.append(action)
            except NotFound:
                continue
            except Exception:
                logger.exception("Error while fetching amendement %r", numero)
                errored.append(str(numero))
                continue
            if numero > max_num_seen:
                max_num_seen = numero
        return actions, errored

    def _collect_amendement(
        self,
        lecture: Lecture,
        numero_prefixe: str,
        position: Optional[int],
        id_discussion_commune: Optional[int] = None,
        id_identique: Optional[int] = None,
    ) -> Tuple[Optional["Amendement"], Optional["Action"]]:
        """
        Récupère un amendement depuis son numéro.
        """
        logger.info("Récupération de l'amendement %r", numero_prefixe)
        amend_data = _retrieve_amendement(lecture, numero_prefixe)
        article = _get_article(lecture, amend_data)
        amendement, action = self.inspect_amendement(
            lecture, article, amend_data, position, id_discussion_commune, id_identique
        )
        return amendement, action

    def inspect_amendement(
        self,
        lecture: Lecture,
        article: Article,
        amend_data: "ANAmendementData",
        position: Optional[int],
        id_discussion_commune: Optional[int],
        id_identique: Optional[int],
    ) -> Tuple[Optional["Amendement"], Optional["Action"]]:

        parent_num_raw = amend_data.get_parent_raw_num()

        num = amend_data.get_num()
        rectif = amend_data.get_rectif()

        matricule = amend_data.get_matricule()
        groupe = amend_data.get_groupe()
        auteur = amend_data.get_auteur()

        mission_ref = amend_data.get_mission_ref()
        mission_titre = mission_ref.titre if mission_ref else None
        mission_titre_court = mission_ref.titre_court if mission_ref else None

        corps = amend_data.get_corps()
        expose = amend_data.get_expose()
        sort = amend_data.get_sort()

        amendement = self.find_existing_amendement(lecture, num)

        action: Optional["Action"] = None

        if amendement is None:
            action = CreateAmendement(
                article=article,
                parent_num_raw=parent_num_raw,
                num=num,
                rectif=rectif,
                position=position,
                id_discussion_commune=id_discussion_commune,
                id_identique=id_identique,
                matricule=matricule,
                groupe=groupe,
                auteur=auteur,
                mission_titre=mission_titre,
                mission_titre_court=mission_titre_court,
                corps=corps,
                expose=expose,
                sort=sort,
            )
            return amendement, action

        old_parent_num_raw = str(amendement.parent.num) if amendement.parent else ""

        modified = any(
            [
                article != amendement.article,
                parent_num_raw != old_parent_num_raw,
                rectif != amendement.rectif,
                corps != amendement.corps,
                expose != amendement.expose,
                sort != amendement.sort,
                id_discussion_commune != amendement.id_discussion_commune,
                id_identique != amendement.id_identique,
                matricule != amendement.matricule,
                groupe != amendement.groupe,
                auteur != amendement.auteur,
                mission_titre != amendement.mission_titre,
                mission_titre_court != amendement.mission_titre_court,
                corps != amendement.corps,
                expose != amendement.expose,
                sort != amendement.sort,
            ]
        )
        if modified:
            action = UpdateAmendement(
                amendement=amendement,
                article=article,
                parent_num_raw=parent_num_raw,
                rectif=rectif,
                position=position,
                id_discussion_commune=id_discussion_commune,
                id_identique=id_identique,
                matricule=matricule,
                groupe=groupe,
                auteur=auteur,
                mission_titre=mission_titre,
                mission_titre_court=mission_titre_court,
                corps=corps,
                expose=expose,
                sort=sort,
            )
        return amendement, action

    def find_existing_amendement(
        self, lecture: Lecture, num: int
    ) -> Optional[Amendement]:
        try:
            return Amendement.get(lecture=lecture, num=num)
        except NoResultFound:
            return None

    def _set_fetch_progress(self, lecture: Lecture, position: int, total: int) -> None:
        total = total + MAX_404
        lecture.set_fetch_progress(position, total)

    def _apply(self, lecture: Lecture, changes: CollectedChanges) -> FetchResult:
        result = FetchResult.create(errored=changes.errored)

        # Build amendement -> position map
        moved_amendements = {
            amendement: changes.position_changes[amendement.num]
            for amendement in lecture.amendements
            if amendement.num in changes.position_changes
        }

        # Reset positions first, so that we never have two with the same position
        # (which would trigger an integrity error due to the unique constraint)
        for amendement in moved_amendements:
            amendement.position = None
        DBSession.flush()

        # Create or update amendements
        for action in changes.actions:
            result += action.apply(lecture)

        # Apply new amendement positions
        for amendement, position in moved_amendements.items():
            if amendement.position != position:
                amendement.position = position

        DBSession.flush()

        return result


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


def fetch_discussion_list(lecture: Lecture) -> "ANDerouleurData":
    """
    Récupère la liste ordonnée des amendements soumis à la discussion.

    Les amendements irrecevables ou encore en traitement ne sont pas inclus.
    """
    url = build_url(lecture)
    content = _retrieve_content(url, force_list=_FORCE_LIST_KEYS_LISTE)
    return ANDerouleurData(lecture, content)


_FORCE_LIST_KEYS_AMENDEMENT = ("programmeAmdt",)


def _retrieve_amendement(lecture: Lecture, numero_prefixe: str) -> "ANAmendementData":
    url = _build_amendement_url(lecture, numero_prefixe)
    try:
        content = _retrieve_content(url, force_list=_FORCE_LIST_KEYS_AMENDEMENT)
    except NotFound:
        url = build_url(lecture, numero_prefixe, fallback=True)
        content = _retrieve_content(url)
    return ANAmendementData(content)


def _build_amendement_url(
    lecture: Lecture, numero_prefixe: str = "", fallback: bool = False
) -> str:
    return build_url(lecture, numero_prefixe, fallback)


def _get_article(lecture: Lecture, amend_data: "ANAmendementData") -> Article:
    subdiv = amend_data.get_division()
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


class ANDerouleurData:
    """
    Data extaction for Assemblée Nationale dérouleur
    """

    def __init__(self, lecture: Lecture, content: dict):
        self.lecture = lecture
        self.content = content

    @reify
    def discussion_items(self) -> List[OrderedDict]:
        try:
            items: List[OrderedDict] = (
                self.content["amdtsParOrdreDeDiscussion"]["amendements"]["amendement"]
            )
            return items
        except TypeError:
            return []

    def find_prefix(self) -> str:
        if self.discussion_items:
            numero_prefixe = self.discussion_items[0]["@numero"]
            prefix, _ = self.parse_num_in_liste(numero_prefixe)
            return prefix
        return get_organe_prefix(self.lecture.organe)

    @property
    def discussion_nums(self) -> Set[int]:
        return {self.parse_num_in_liste(d["@numero"])[1] for d in self.discussion_items}

    @classmethod
    def parse_num_in_liste(cls, num_long: str) -> Tuple[str, int]:
        mo = cls._RE_NUM.match(num_long)
        if mo is None:
            raise ValueError(f"Cannot parse amendement number {num_long!r}")
        return mo.group("acronyme"), int(mo.group("num"))

    _RE_NUM = re.compile(r"(?P<acronyme>[A-Z]*)(?P<num>\d+)")

    def updated_amendement_positions(self) -> Dict[int, Optional[int]]:

        amendements = [amdt for amdt in self.lecture.amendements]

        current_order = {amdt.num: amdt.position for amdt in amendements}

        new_order = {
            self.parse_num_in_liste(item["@numero"])[1]: index
            for index, item in enumerate(self.discussion_items, start=1)
        }

        for amdt in amendements:
            if amdt.num not in current_order:
                logger.error("%r not in %r", amdt.num, current_order)
                raise ValueError

        return {
            amdt.num: new_order.get(amdt.num)
            for amdt in amendements
            if new_order.get(amdt.num) != current_order[amdt.num]
        }


def get_organe_abrev(organe_uid: str) -> str:
    from zam_repondeur.services.data import repository

    organe = repository.get_opendata_organe(organe_uid)
    if organe is None:
        raise OrganeNotFound(organe)
    abrev: str = organe["libelleAbrev"]
    return abrev


class Action(ABC):
    @abstractmethod
    def apply(self, lecture: Lecture) -> FetchResult:
        pass


class CreateOrUpdateAmendement(Action):
    def __init__(
        self,
        article: Article,
        parent_num_raw: str,
        rectif: int,
        position: Optional[int],
        id_discussion_commune: Optional[int],
        id_identique: Optional[int],
        matricule: str,
        groupe: str,
        auteur: str,
        mission_titre: Optional[str],
        mission_titre_court: Optional[str],
        corps: str,
        expose: str,
        sort: str,
    ):
        self.article = article
        self.parent_num_raw = parent_num_raw
        self.rectif = rectif
        self.position = position
        self.id_discussion_commune = id_discussion_commune
        self.id_identique = id_identique
        self.matricule = matricule
        self.groupe = groupe
        self.auteur = auteur
        self.mission_titre = mission_titre
        self.mission_titre_court = mission_titre_court
        self.corps = corps
        self.expose = expose
        self.sort = sort

    def _get_parent(self, lecture: Lecture) -> Optional[Amendement]:
        parent_num, parent_rectif = Amendement.parse_num(self.parent_num_raw)
        if not parent_num:
            return None
        parent: Optional[Amendement]
        parent, _ = get_one_or_create(
            Amendement,
            create_kwargs={"article": self.article, "rectif": parent_rectif},
            lecture=lecture,
            num=parent_num,
        )
        return parent


class CreateAmendement(CreateOrUpdateAmendement):
    def __init__(self, num: int, **kwargs: Any):
        super().__init__(**kwargs)
        self.num = num

    def __repr__(self) -> str:
        return f"<CreateAmendement(num={self.num})>"

    def apply(self, lecture: Lecture) -> FetchResult:
        parent = self._get_parent(lecture)
        amendement = Amendement.create(
            lecture=lecture,
            article=self.article,
            parent=parent,
            position=self.position,
            num=self.num,
            rectif=self.rectif,
            id_discussion_commune=self.id_discussion_commune,
            id_identique=self.id_identique,
            matricule=self.matricule,
            groupe=self.groupe,
            auteur=self.auteur,
            mission_titre=self.mission_titre,
            mission_titre_court=self.mission_titre_court,
            corps=self.corps,
            expose=self.expose,
            sort=self.sort,
        )

        return FetchResult.create(amendements=[amendement], created=1)


class UpdateAmendement(CreateOrUpdateAmendement):
    def __init__(self, amendement: Amendement, **kwargs: Any):
        super().__init__(**kwargs)
        self.amendement = amendement

    def __repr__(self) -> str:
        return f"<UpdateAmendement(num={self.amendement.num})>"

    def apply(self, lecture: Lecture) -> FetchResult:
        parent = self._get_parent(lecture)

        if (
            self.amendement.location.batch
            and self.amendement.article.pk != self.article.pk
        ):
            BatchUnset.create(amendement=self.amendement, request=None)

        Source.update_rectif(self.amendement, self.rectif)
        Source.update_corps(self.amendement, self.corps)
        Source.update_expose(self.amendement, self.expose)
        Source.update_sort(self.amendement, self.sort)
        Source.update_attributes(
            self.amendement,
            article=self.article,
            parent=parent,
            position=self.position,
            id_discussion_commune=self.id_discussion_commune,
            id_identique=self.id_identique,
            matricule=self.matricule,
            groupe=self.groupe,
            auteur=self.auteur,
            mission_titre=self.mission_titre,
            mission_titre_court=self.mission_titre_court,
        )

        return FetchResult.create(amendements=[self.amendement])


class LigneCredits(NamedTuple):
    libelle: str
    pos: str
    neg: str


class TableauCredits(NamedTuple):
    programmes: List[LigneCredits]
    totaux: LigneCredits
    solde: str


class ANAmendementData:
    """
    Data extaction for Assemblée Nationale amendement
    """

    def __init__(self, content: dict):
        self.amend = content["amendement"]

    def get_num(self) -> int:
        return int(self.amend["numero"])

    def get_rectif(self) -> int:
        numero_long = self._get_str_or_none("numeroLong")
        if numero_long is None:
            return 0
        return self.parse_numero_long_with_rect(numero_long)

    @classmethod
    def parse_numero_long_with_rect(cls, text: str) -> int:
        mo = cls._RE_NUM_LONG.match(text)
        if mo is not None and mo.group("rect"):
            return int(mo.group("rect_mult") or 1)
        return 0

    _RE_NUM_LONG = re.compile(
        r"""
        (?P<prefix>[A-Z]*)
        (?P<num>\d+)
        (?P<rect>\s\((?:(?P<rect_mult>\d+)\w+\s)?Rect\))?
        """,
        re.VERBOSE,
    )

    def get_parent_raw_num(self) -> str:
        return self._get_str_or_none("numeroParent") or ""

    def get_division(self) -> SubDiv:
        division: Optional[Any] = self.amend["division"]
        if not isinstance(division, dict):
            raise ValueError("Invalid division key")
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

    @reify
    def raw_auteur(self) -> Optional[dict]:
        raw_auteur: Optional[Any] = self.amend.get("auteur")
        if raw_auteur is None:
            logger.warning("Unknown auteur for amendement %s", self.get_num())
            return None
        if not isinstance(raw_auteur, dict):
            raise ValueError("Invalid type for auteur key")
        return raw_auteur

    def get_matricule(self) -> str:
        if self.raw_auteur is None:
            return ""
        return self.raw_auteur.get("tribunId", "")

    def get_auteur(self) -> str:
        if self.raw_auteur is None:
            return "Non trouvé"
        if self.raw_auteur.get("estGouvernement", "") == "1":
            return "LE GOUVERNEMENT"
        nom = self.raw_auteur.get("nom", "")
        prenom = self.raw_auteur.get("prenom", "")
        return f"{nom} {prenom}"

    def get_groupe(self) -> str:
        from zam_repondeur.services.data import repository

        if self.raw_auteur is None:
            return "Non trouvé"

        gouvernemental = bool(int(self.raw_auteur["estGouvernement"]))
        rapporteur = bool(int(self.raw_auteur["estRapporteur"]))
        if gouvernemental or rapporteur:
            return ""

        groupe_tribun_id = self._get_str_or_none(
            "groupeTribunId", dict_=self.raw_auteur
        )
        if groupe_tribun_id is None:
            logger.warning(
                "Missing groupeTribunId value for amendement %s", self.get_num()
            )
            return "Non précisé"

        groupe = repository.get_opendata_organe(f"PO{groupe_tribun_id}")
        if groupe is None:
            logger.warning(
                "Unknown groupe tribun 'PO%s' in groupes for amendement %s",
                groupe_tribun_id,
                self.get_num(),
            )
            return "Non trouvé"

        libelle: str = groupe["libelle"]
        return libelle

    def get_corps(self) -> str:
        if "listeProgrammesAmdt" in self.amend:
            return self.render_credits_tables()
        else:
            return self._unjustify(self._get_str_or_none("dispositif") or "")

    def get_expose(self) -> str:
        return self._unjustify(self._get_str_or_none("exposeSommaire") or "")

    def render_credits_tables(self) -> str:
        ae = self._extract_credits_table(type_credits="aE")
        cp = self._extract_credits_table(type_credits="cP")
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

    def _extract_credits_table(self, type_credits: str) -> TableauCredits:
        programmes = self.amend["listeProgrammesAmdt"]["programmeAmdt"]

        new_format = "aEPositifFormat" in programmes[0]
        if new_format:
            pos_key, neg_key = "Positif", "Negatif"
        else:
            pos_key, neg_key = "SupplementairesOuvertes", "Annulees"

        return TableauCredits(
            programmes=[
                LigneCredits(
                    libelle=self._extract_libelle(programme),
                    pos=programme[type_credits + pos_key + "Format"],
                    neg=programme[type_credits + neg_key + "Format"],
                )
                for programme in programmes
            ],
            totaux=LigneCredits(
                libelle="Totaux",
                pos=self.amend["total" + type_credits.upper() + pos_key + "Format"],
                neg=self.amend["total" + type_credits.upper() + neg_key + "Format"],
            ),
            solde=self.amend["solde" + type_credits.upper() + "Format"],
        )

    def _extract_libelle(self, programme: OrderedDict) -> str:
        libelle: str = programme["libelleProgrammeAmdt"]
        if programme["programmeAmdtNouveau"] == "true":
            libelle += " (ligne nouvelle)"
        return libelle

    def get_sort(self) -> str:
        sort = self._get_str_or_none("sortEnSeance")
        if sort is not None:
            return sort.lower()
        if (
            self.amend["retireAvantPublication"] == "1"
            or self.amend.get("retireApresPublication", "0") == "1"
        ):
            return "Retiré"
        etat = self._get_str_or_none("etat")
        if etat not in self._ETATS_OK:
            return "Irrecevable"
        return ""

    _ETATS_OK = {
        "AT",  # à traiter
        "T",  # traité
        "ER",  # en recevabilité
        "R",  # recevable
        "AC",  # à discuter
        "DI",  # discuté
    }

    def get_mission_ref(self) -> Optional[MissionRef]:
        if "missionVisee" not in self.amend:
            return None
        mission_visee = self._get_str_or_none("missionVisee")
        if mission_visee is None:
            return None
        return self.parse_mission_visee(mission_visee)

    @classmethod
    def parse_mission_visee(cls, mission_visee: str) -> MissionRef:
        mo = cls._RE_MISSION_VISEE.match(mission_visee)
        titre_court = mo.group("titre_court") if mo is not None else mission_visee
        return MissionRef(titre=mission_visee, titre_court=titre_court)

    _RE_MISSION_VISEE = re.compile(r"""(Mission )?« (?P<titre_court>.*) »""")

    def _get_str_or_none(self, key: str, dict_: Optional[dict] = None) -> Optional[str]:
        if dict_ is None:
            dict_ = self.amend
        value = dict_[key]
        if isinstance(value, str):
            return value
        if isinstance(value, dict) and value.get("@xsi:nil") == "true":
            return None
        raise ValueError(f"Unexpected value {value!r} for key {key!r}")

    @staticmethod
    def _unjustify(content: str) -> str:
        return content.replace(' style="text-align: justify;"', "")
