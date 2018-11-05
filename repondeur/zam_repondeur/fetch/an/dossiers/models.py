from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import List, Optional


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


class TypeTexte(Enum):
    PROJET = "Projet de loi"
    PROPOSITION = "Proposition de loi"

    @staticmethod
    def from_dict(texte: dict) -> "TypeTexte":
        code = texte["classification"]["type"]["code"]
        if code == "PRJL":
            return TypeTexte.PROJET
        if code == "PION":
            return TypeTexte.PROPOSITION
        raise ValueError(f"Unknown texte type {code}")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}.{self.name}"


@dataclass
class Texte:
    uid: str
    type_: TypeTexte
    numero: int
    titre_long: str
    titre_court: str
    date_depot: date


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


@dataclass
class Dossier:
    uid: str
    titre: str
    lectures: List[Lecture]
