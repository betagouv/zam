from typing import Any, List, NamedTuple

from zam_repondeur.models import Amendement, Lecture


class Source:
    def update_attributes(self, amendement: Amendement, **values: Any) -> bool:
        modified = False
        for name, value in values.items():
            if getattr(amendement, name) != value:
                setattr(amendement, name, value)
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
    def get_remote_source_for_chambre(cls, chambre: str) -> "RemoteSource":
        from zam_repondeur.fetch.an.amendements import AssembleeNationale
        from zam_repondeur.fetch.senat.amendements import Senat

        if chambre == "an":
            return AssembleeNationale()
        elif chambre == "senat":
            return Senat()
        else:
            raise NotImplementedError


def get_amendements(lecture: Lecture) -> FetchResult:
    source = RemoteSource.get_remote_source_for_chambre(lecture.chambre)
    return source.fetch(lecture)
