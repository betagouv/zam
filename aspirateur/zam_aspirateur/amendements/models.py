import re
from dataclasses import asdict, dataclass, replace
from datetime import date
from typing import Optional


@dataclass
class Amendement:

    # Identification du texte
    chambre: str  # 'senat' or 'an'
    session: str  # session / législature
    num_texte: str  # numéro de texte / lecture

    subdiv_type: str  # article, titre...
    subdiv_num: str  # numéro
    subdiv_mult: str = ""  # bis, ter...
    subdiv_pos: str = ""  # avant / après

    alinea: str = ""  # libellé de l'alinéa de l'article concerné

    num: str = ""  # numéro de l'amendement

    rectif: int = 0  # numéro de révision de l'amendement

    auteur: str = ""
    matricule: Optional[str] = None
    groupe: str = ""  # groupe parlementaire

    date_depot: Optional[date] = None

    sort: Optional[str] = None  # retiré, adopté, etc.

    position: Optional[int] = None  # ordre de lecture
    discussion_commune: Optional[int] = None
    identique: Optional[bool] = None

    dispositif: Optional[str] = None  # texte de l'amendement
    objet: Optional[str] = None  # motivation

    resume: Optional[str] = None  # résumé de l'objet

    avis: Optional[str] = None  # position du gouvernemnt
    observations: Optional[str] = None
    reponse: Optional[str] = None

    @property
    def num_int(self) -> int:
        """
        Numéro d'amendement sous forme purement numérique (sans suffixes)
        """
        mo = re.search(r"(\d+)", self.num)
        assert mo is not None
        return int(mo.group(1))

    @property
    def num_disp(self) -> str:
        return f"{self.num}{self._RECT_SUFFIXES[self.rectif]}"

    _RECT_SUFFIXES = {
        0: "",
        1: " rect",
        2: " rect bis",
        3: " rect ter",
        4: " rect quater",
        5: " rect quinquies",
        6: " rect sexies",
        7: " rect septies",
        8: " rect octies",
        9: " rect nonies",
        10: " rect decies",
    }

    @property
    def gouvernemental(self) -> bool:
        return self.auteur == "LE GOUVERNEMENT"

    def replace(self, changes: dict) -> "Amendement":
        amendement = replace(self, **changes)  # type: Amendement
        return amendement

    def asdict(self) -> dict:
        dict_ = asdict(self)  # type: dict
        return dict_
