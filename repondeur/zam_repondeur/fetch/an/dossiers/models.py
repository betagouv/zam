from copy import copy, deepcopy
from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Dict, List, Optional, Tuple

from zam_repondeur.models.texte import TypeTexte


class ChambreRef(Enum):
    AN = "an"
    SENAT = "senat"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}.{self.name}"

    def __str__(self) -> str:
        if self.value == "an":
            return "Assemblée nationale"
        if self.value == "senat":
            return "Sénat"
        raise NotImplementedError


@dataclass(eq=True, frozen=True)
class TexteRef:
    uid: str
    type_: TypeTexte
    chambre: ChambreRef
    legislature: Optional[int]
    numero: int
    titre_long: str
    titre_court: str
    date_depot: Optional[date]

    @property
    def session(self) -> Optional[int]:
        if self.chambre == ChambreRef.AN:
            return None
        if not self.date_depot:
            raise NotImplementedError
        # The session changes the first working day of October.
        if self.date_depot.month >= 10:
            return self.date_depot.year
        else:
            return self.date_depot.year - 1


@dataclass
class LectureRef:
    chambre: ChambreRef
    titre: str
    texte: TexteRef
    organe: str
    partie: Optional[int] = None

    @property
    def key(self) -> str:
        return f"{self.texte.uid}-{self.organe}-{self.partie or ''}"

    @property
    def label(self) -> str:
        if self.partie == 1:
            partie = " (première partie)"
        elif self.partie == 2:
            partie = " (seconde partie)"
        else:
            partie = ""
        return f"{self.chambre} – {self.titre} – Texte Nº {self.texte.numero}{partie}"

    @property
    def cmp_key(self) -> Tuple[ChambreRef, str, int, Optional[int]]:
        return (self.chambre, self.organe, self.texte.numero, self.partie)


MIN_DATE = date(1900, 1, 1)


DossierRefsByUID = Dict[str, "DossierRef"]


@dataclass
class DossierRef:
    uid: str
    titre: str
    lectures: List[LectureRef]

    @property
    def most_recent_texte_date(self) -> date:
        return max(
            (lecture.texte.date_depot or MIN_DATE for lecture in self.lectures),
            default=MIN_DATE,
        )

    @classmethod
    def merge_dossiers(
        cls, dossiers: DossierRefsByUID, others: DossierRefsByUID
    ) -> DossierRefsByUID:
        return {
            uid: (
                dossiers.get(uid, DossierRef(uid, "", []))
                + others.get(uid, DossierRef(uid, "", []))
            )
            for uid in dossiers.keys() | others.keys()
        }

    def __add__(self, other: "DossierRef") -> "DossierRef":
        if not isinstance(other, DossierRef):
            raise NotImplementedError
        if other.uid != self.uid:
            raise ValueError
        return DossierRef(
            uid=self.uid,
            titre=self.titre or other.titre,
            lectures=self._merge_lectures(other.lectures),
        )

    def _merge_lectures(self, other_lectures: List[LectureRef]) -> List[LectureRef]:
        return deepcopy(self.lectures) + [
            copy(lecture)
            for lecture in other_lectures
            if not any(l.cmp_key == lecture.cmp_key for l in self.lectures)
        ]
