import re
from dataclasses import asdict, dataclass, replace
from datetime import date
from typing import NamedTuple, Optional, Tuple


@dataclass
class Amendement:

    # Identification du texte
    chambre: str  # 'senat' or 'an'
    session: str  # session / législature
    num_texte: int  # numéro de texte / lecture

    subdiv_type: str  # article, titre...
    subdiv_num: str  # numéro
    subdiv_mult: str = ""  # bis, ter...
    subdiv_pos: str = ""  # avant / après

    alinea: str = ""  # libellé de l'alinéa de l'article concerné

    num: int = 0  # numéro de l'amendement
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
    def num_disp(self) -> str:
        text = str(self.num)
        if self.rectif > 0:
            text += " rect."
        if self.rectif > 1:
            if self.rectif not in self._RECTIF_TO_SUFFIX:
                raise NotImplementedError
            text += " "
            text += self._RECTIF_TO_SUFFIX[self.rectif]
        return text

    _RECTIF_TO_SUFFIX = {
        2: "bis",
        3: "ter",
        4: "quater",
        5: "quinquies",
        6: "sexies",
        7: "septies",
        8: "octies",
        9: "nonies",
        10: "decies",
    }

    _SUFFIX_TO_RECTIF = {suffix: rectif for rectif, suffix in _RECTIF_TO_SUFFIX.items()}

    _NUM_RE = re.compile(r"(?P<num>\d+)(?P<rect> rect\.(?: (?P<suffix>\w+))?)?")

    @staticmethod
    def parse_num(text: str) -> Tuple[int, int]:
        mo = Amendement._NUM_RE.match(text)
        if mo is None:
            raise ValueError(f"Cannot parse amendement number '{text}'")
        num = int(mo.group("num"))
        if mo.group("rect") is None:
            rectif = 0
        else:
            suffix = mo.group("suffix")
            if suffix is None:
                rectif = 1
            else:
                if suffix in Amendement._SUFFIX_TO_RECTIF:
                    rectif = Amendement._SUFFIX_TO_RECTIF[suffix]
                else:
                    raise ValueError(f"Cannot parse amendement number '{text}'")
        return (num, rectif)

    @property
    def gouvernemental(self) -> bool:
        return self.auteur == "LE GOUVERNEMENT"

    def replace(self, changes: dict) -> "Amendement":
        amendement = replace(self, **changes)  # type: Amendement
        return amendement

    def asdict(self) -> dict:
        dict_ = asdict(self)  # type: dict
        return dict_


class SubDiv(NamedTuple):
    type_: str
    num: str
    mult: str
    pos: str
