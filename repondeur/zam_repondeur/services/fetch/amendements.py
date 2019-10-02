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
    def update_attributes(self, amendement: Amendement, **values: Any) -> bool:
        modified = False
        for name, value in values.items():
            if getattr(amendement, name) != value:
                setattr(amendement, name, value)
                modified = True
        return modified

    def update_rectif(self, amendement: Amendement, rectif: int) -> bool:
        modified = False
        if rectif != amendement.rectif:
            AmendementRectifie.create(amendement=amendement, rectif=rectif)
            modified = True
        return modified

    def update_sort(self, amendement: Amendement, sort: str) -> bool:
        modified = False
        if sort != amendement.sort:
            if "irrecevable" in sort.lower():
                AmendementIrrecevable.create(amendement=amendement, sort=sort)
                # Put the amendement back to the index?
                if amendement.user_table is not None:
                    AmendementTransfere.create(
                        amendement=amendement,
                        old_value=str(amendement.user_table.user),
                        new_value="",
                    )
                    amendement.user_table = None
            else:
                amendement.sort = sort
            modified = True
        return modified

    def update_corps(self, amendement: Amendement, corps: str) -> bool:
        modified = False
        if corps != amendement.corps:
            CorpsAmendementModifie.create(amendement=amendement, corps=corps)
            modified = True
        return modified

    def update_expose(self, amendement: Amendement, expose: str) -> bool:
        modified = False
        if expose != amendement.expose:
            ExposeAmendementModifie.create(amendement=amendement, expose=expose)
            modified = True
        return modified


class FetchResult(NamedTuple):
    amendements: List[Amendement]
    created: int
    errored: List[str]

    def __add__(self: "FetchResult", other: object) -> "FetchResult":
        if not isinstance(other, FetchResult):
            raise TypeError
        return FetchResult(
            amendements=self.amendements + other.amendements,
            created=self.created + other.created,
            errored=self.errored + other.errored,
        )


class RemoteSource(Source):
    def fetch(self, lecture: Lecture) -> FetchResult:
        raise NotImplementedError

    @classmethod
    def get_remote_source_for_chambre(cls, chambre: Chambre) -> "RemoteSource":
        from zam_repondeur.services.fetch.an.amendements import AssembleeNationale
        from zam_repondeur.services.fetch.senat.amendements import Senat

        if chambre == Chambre.AN:
            return AssembleeNationale()
        if chambre == Chambre.SENAT:
            return Senat()
        raise NotImplementedError


def get_amendements(lecture: Lecture) -> FetchResult:
    source = RemoteSource.get_remote_source_for_chambre(lecture.chambre)
    return source.fetch(lecture)
