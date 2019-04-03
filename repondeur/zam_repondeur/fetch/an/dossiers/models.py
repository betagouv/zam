from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import List, Optional

from zam_repondeur.models.texte import TypeTexte


class Chambre(Enum):
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
class Texte:
    uid: str
    type_: TypeTexte
    numero: int
    titre_long: str
    titre_court: str
    date_depot: Optional[date]


@dataclass
class Lecture:
    chambre: Chambre
    titre: str
    texte: Texte
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

    def get_session(self) -> str:
        if self.chambre == Chambre.AN:
            return "15"  # FIXME
        else:
            if not self.texte.date_depot:
                return "2017-2018"  # FIXME: sane default?
            # The session changes the first working day of October.
            if self.texte.date_depot.month >= 10:
                year = self.texte.date_depot.year
            else:
                year = self.texte.date_depot.year - 1
            return f"{year}-{year + 1}"


@dataclass
class Dossier:
    uid: str
    titre: str
    lectures: List[Lecture]
