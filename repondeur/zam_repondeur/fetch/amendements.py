from typing import List, NamedTuple

from zam_repondeur.fetch.an.amendements import aspire_an
from zam_repondeur.fetch.senat.amendements import aspire_senat
from zam_repondeur.models import Amendement, Lecture


class Source:
    pass


class FetchResult(NamedTuple):
    amendements: List[Amendement]
    created: int
    errored: List[str]


class RemoteSource(Source):

    def fetch(self, lecture: Lecture) -> FetchResult:
        raise NotImplementedError

    @classmethod
    def get_remote_source_for_chambre(cls, chambre: str) -> "RemoteSource":
        if chambre == "an":
            return AssembleeNationale()
        elif chambre == "senat":
            return Senat()
        else:
            raise NotImplementedError


class AssembleeNationale(RemoteSource):
    def fetch(self, lecture: Lecture) -> FetchResult:
        amendements, created, errored = aspire_an(lecture=lecture)
        return FetchResult(amendements, created, errored)


class Senat(RemoteSource):
    def fetch(self, lecture: Lecture) -> FetchResult:
        amendements, created = aspire_senat(lecture=lecture)
        return FetchResult(amendements, created, [])


def get_amendements(lecture: Lecture) -> FetchResult:
    source = RemoteSource.get_remote_source_for_chambre(lecture.chambre)
    return source.fetch(lecture)
