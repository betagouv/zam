from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import List


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

    @property
    def label(self) -> str:
        return (
            f"{self.chambre} – {self.titre} "
            f"(texte nº\u00a0{self.texte.numero} "
            f"déposé le {self.texte.date_depot.strftime('%d/%m/%Y')})"
        )


@dataclass
class Dossier:
    uid: str
    titre: str
    lectures: List[Lecture]
