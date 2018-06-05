import re
from dataclasses import asdict, dataclass, replace
from datetime import date
from typing import Optional


@dataclass
class Amendement:

    subdiv_type: int  # article, titre...
    subdiv_num: int  # numéro
    subdiv_mult: str = ""  # bis, ter...
    subdiv_pos: str = ""  # avant / après

    alinea: str = ""  # libellé de l'alinéa de l'article concerné

    num: str = ""  # numéro de l'amendement
    rectif: int = 0  # numéro de révision de l'amendement

    auteur: str = ""
    matricule: Optional[str] = None
    groupe: Optional[str] = None  # groupe parlementaire

    date_depot: Optional[date] = None

    sort: Optional[str] = None  # retiré, adopté, etc.

    discussion_commune: Optional[bool] = None
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
    def gouvernemental(self) -> bool:
        return self.auteur == "LE GOUVERNEMENT"

    def replace(self, **changes: dict) -> "Amendement":
        amendement = replace(self, **changes)  # type: Amendement
        return amendement

    def asdict(self) -> dict:
        dict_ = asdict(self)  # type: dict
        return dict_
