from typing import Any, List, NamedTuple

from zam_repondeur.models import Amendement, Chambre, Lecture
from zam_repondeur.models.events.amendement import (
    AmendementIrrecevable,
    AmendementRectifie,
    AmendementTransfere,
    CorpsAmendementModifie,
    ExposeAmendementModifie,
)


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
    amendements: List[Amendement]
    created: int
    errored: List[str]

    @classmethod
    def create(
        cls,
        amendements: List[Amendement] = [],
        created: int = 0,
        errored: List[str] = [],
    ) -> "FetchResult":
        return cls(amendements=amendements, created=created, errored=errored)

    def __add__(self: "FetchResult", other: object) -> "FetchResult":
        if not isinstance(other, FetchResult):
            raise TypeError
        return FetchResult(
            amendements=self.amendements + other.amendements,
            created=self.created + other.created,
            errored=self.errored + other.errored,
        )


class RemoteSource(Source):
    def __init__(self, prefetching_enabled: bool = True):
        self.prefetching_enabled = prefetching_enabled

    def prepare(self, lecture: Lecture) -> None:
        pass

    def fetch(self, lecture: Lecture) -> FetchResult:
        raise NotImplementedError

    @classmethod
    def get_remote_source_for_chambre(
        cls, chambre: Chambre, prefetching_enabled: bool = True
    ) -> "RemoteSource":
        from zam_repondeur.services.fetch.an.amendements import AssembleeNationale
        from zam_repondeur.services.fetch.senat.amendements import Senat

        if chambre == Chambre.AN:
            return AssembleeNationale(prefetching_enabled=prefetching_enabled)
        if chambre == Chambre.SENAT:
            return Senat(prefetching_enabled=prefetching_enabled)
        raise NotImplementedError
