from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Dict


class Chambre(Enum):
    AN = "an"
    SENAT = "senat"

    def __str__(self) -> str:
        if self.value == "an":
            return "Assemblée nationale"
        if self.value == "senat":
            return "Sénat"
        raise NotImplementedError


class TypeTexte(Enum):
    PROJET = "Projet de loi"
    PROPOSITION = "Proposition de loi"


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


@dataclass
class Dossier:
    uid: str
    titre: str
    lectures: Dict[str, Lecture]
