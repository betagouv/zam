import logging
from abc import ABC, abstractmethod
from datetime import date
from typing import Any, Dict, Iterable, List, NamedTuple, Optional, Set

from zam_repondeur.models import (
    Amendement,
    Article,
    Chambre,
    Lecture,
    get_one_or_create,
)
from zam_repondeur.models.division import SubDiv
from zam_repondeur.models.events.amendement import (
    AmendementIrrecevable,
    AmendementRectifie,
    AmendementTransfere,
    BatchUnset,
    CorpsAmendementModifie,
    ExposeAmendementModifie,
)

logger = logging.getLogger(__name__)


class Source:
    @staticmethod
    def update_attributes(amendement: Amendement, **values: Any) -> None:
        for name, value in values.items():
            if getattr(amendement, name) != value:
                setattr(amendement, name, value)

    @staticmethod
    def update_rectif(amendement: Amendement, rectif: int) -> None:
        if rectif != amendement.rectif:
            AmendementRectifie.create(amendement=amendement, rectif=rectif)

    @staticmethod
    def update_sort(amendement: Amendement, sort: str) -> None:
        if sort != amendement.sort:
            if "irrecevable" in sort.lower():
                AmendementIrrecevable.create(amendement=amendement, sort=sort)
                # Put the amendement back to the index?
                if amendement.location.user_table is not None:
                    AmendementTransfere.create(
                        amendement=amendement,
                        old_value=str(amendement.location.user_table.user),
                        new_value="",
                    )
                    amendement.location.user_table = None
            else:
                amendement.sort = sort

    @staticmethod
    def update_corps(amendement: Amendement, corps: str) -> None:
        if corps != amendement.corps:
            CorpsAmendementModifie.create(amendement=amendement, corps=corps)

    @staticmethod
    def update_expose(amendement: Amendement, expose: str) -> None:
        if expose != amendement.expose:
            ExposeAmendementModifie.create(amendement=amendement, expose=expose)


class FetchResult(NamedTuple):
    fetched: Set[int]
    created: Set[int]
    errored: Set[int]
    next_start_index: Optional[int]

    @property
    def changed(self) -> bool:
        return bool(self.fetched and not (self.created or self.errored))

    @classmethod
    def create(
        cls,
        fetched: Iterable[int] = (),
        created: Iterable[int] = (),
        errored: Iterable[int] = (),
        next_start_index: Optional[int] = None,
    ) -> "FetchResult":
        return cls(
            fetched=set(fetched),
            created=set(created),
            errored=set(errored),
            next_start_index=next_start_index,
        )

    def __add__(self: "FetchResult", other: object) -> "FetchResult":  # type: ignore
        if not isinstance(other, FetchResult):
            raise TypeError
        if other.next_start_index is None:
            next_start_index = self.next_start_index
        else:
            next_start_index = other.next_start_index
        return FetchResult(
            fetched=self.fetched | other.fetched,
            created=self.created | other.created,
            errored=self.errored | other.errored,
            next_start_index=next_start_index,
        )


class CollectedChanges(NamedTuple):
    """
    Changes found by the collect phase
    """

    derouleur_fetch_success: bool
    position_changes: Dict[int, Optional[int]]
    actions: List["Action"]
    unchanged: List[int]
    errored: Set[int]
    next_start_index: Optional[int]

    @classmethod
    def create(
        cls,
        derouleur_fetch_success: bool = True,
        position_changes: Optional[Dict[int, Optional[int]]] = None,
        actions: Optional[List["Action"]] = None,
        unchanged: Optional[List[int]] = None,
        errored: Optional[Set[int]] = None,
        next_start_index: Optional[int] = None,
    ) -> "CollectedChanges":
        if position_changes is None:
            position_changes = {}
        if actions is None:
            actions = []
        if unchanged is None:
            unchanged = []
        if errored is None:
            errored = set()
        return cls(
            derouleur_fetch_success,
            position_changes,
            actions,
            unchanged,
            errored,
            next_start_index,
        )


class Action(ABC):
    @abstractmethod
    def apply(self, lecture: Lecture) -> FetchResult:
        pass


class CreateOrUpdateAmendement(Action):
    def __init__(
        self,
        subdiv: SubDiv,
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
        date_depot: Optional[date],
    ):
        self.subdiv = subdiv
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
        self.date_depot = date_depot

    def _get_article(self, lecture: Lecture) -> Article:
        article: Article
        created: bool
        article, created = get_one_or_create(
            Article,
            lecture=lecture,
            type=self.subdiv.type_,
            num=self.subdiv.num,
            mult=self.subdiv.mult,
            pos=self.subdiv.pos,
        )
        return article

    def _get_parent(self, lecture: Lecture, article: Article) -> Optional[Amendement]:
        parent_num, parent_rectif = Amendement.parse_num(self.parent_num_raw)
        if not parent_num:
            return None
        parent: Optional[Amendement]
        parent, _ = get_one_or_create(
            Amendement,
            create_kwargs={"article": article, "rectif": parent_rectif},
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
        article = self._get_article(lecture)
        parent = self._get_parent(lecture, article)

        Amendement.create(
            lecture=lecture,
            article=article,
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
            date_depot=self.date_depot,
        )

        return FetchResult.create(fetched={self.num}, created={self.num})


class UpdateAmendement(CreateOrUpdateAmendement):
    def __init__(self, amendement_num: int, **kwargs: Any):
        super().__init__(**kwargs)
        self.amendement_num = amendement_num

    def __repr__(self) -> str:
        return f"<UpdateAmendement(num={self.amendement_num})>"

    def apply(self, lecture: Lecture) -> FetchResult:
        amendement = lecture.find_amendement(self.amendement_num)
        if amendement is None:
            return FetchResult.create(errored={self.amendement_num})

        article = self._get_article(lecture)
        parent = self._get_parent(lecture, article)

        if amendement.location.batch and amendement.article.pk != article.pk:
            BatchUnset.create(amendement=amendement, request=None)

        Source.update_rectif(amendement, self.rectif)
        Source.update_corps(amendement, self.corps)
        Source.update_expose(amendement, self.expose)
        Source.update_sort(amendement, self.sort)
        Source.update_attributes(
            amendement,
            article=article,
            parent=parent,
            position=self.position,
            id_discussion_commune=self.id_discussion_commune,
            id_identique=self.id_identique,
            matricule=self.matricule,
            groupe=self.groupe,
            auteur=self.auteur,
            mission_titre=self.mission_titre,
            mission_titre_court=self.mission_titre_court,
            date_depot=self.date_depot,
        )

        return FetchResult.create(fetched={self.amendement_num})


class RemoteSource(Source):
    def __init__(self, settings: Dict[str, Any], prefetching_enabled: bool = True):
        self.prefetching_enabled = prefetching_enabled

    def prepare(self, lecture: Lecture) -> None:
        pass

    def fetch(self, lecture: Lecture, start_index: int = 0) -> FetchResult:
        changes = self.collect_changes(lecture, start_index=start_index)
        return self.apply_changes(lecture, changes)

    def collect_changes(
        self, lecture: Lecture, start_index: int = 0
    ) -> CollectedChanges:
        raise NotImplementedError()

    def apply_changes(self, lecture: Lecture, changes: CollectedChanges) -> FetchResult:
        raise NotImplementedError()

    @classmethod
    def get_remote_source_for_chambre(
        cls,
        chambre: Chambre,
        settings: Dict[str, Any],
        prefetching_enabled: bool = True,
    ) -> "RemoteSource":
        from zam_repondeur.services.fetch.an.amendements import AssembleeNationale
        from zam_repondeur.services.fetch.senat.amendements import Senat

        if chambre == Chambre.AN:
            return AssembleeNationale(
                settings=settings, prefetching_enabled=prefetching_enabled
            )
        if chambre == Chambre.SENAT:
            return Senat(settings=settings, prefetching_enabled=prefetching_enabled)
        raise NotImplementedError
