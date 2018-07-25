import re
from dataclasses import asdict, dataclass, fields, replace
from datetime import date, datetime
from typing import Iterable, NamedTuple, Optional, Tuple


@dataclass
class Amendement:

    # Identification du texte
    chambre: str  # 'senat' or 'an'
    session: str  # session / législature
    num_texte: int  # numéro de texte / lecture
    organe: str  # assemblée, commission...

    subdiv_type: str  # article, titre...
    subdiv_num: str  # numéro
    subdiv_mult: str = ""  # bis, ter...
    subdiv_pos: str = ""  # avant / après
    subdiv_titre: str = ""  # titre article
    subdiv_contenu: str = ""  # contenu article

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
    parent_num: Optional[int] = 0  # sous-amendement
    parent_rectif: Optional[int] = 0  # sous-amendement

    dispositif: Optional[str] = None  # texte de l'amendement
    objet: Optional[str] = None  # motivation

    resume: Optional[str] = None  # résumé de l'objet

    avis: Optional[str] = None  # position du gouvernemnt
    observations: Optional[str] = None
    reponse: Optional[str] = None

    bookmarked_at: Optional[datetime] = None

    @property
    def parent(self) -> Optional["Amendement"]:
        if not self.parent_num:
            return None

        from zam_repondeur.models import DBSession

        parent: Optional[Amendement] = (
            DBSession.query(Amendement)
            .filter(
                Amendement.num == self.parent_num,
                Amendement.rectif == self.parent_rectif,
            )
            .first()
        )
        return parent

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

    @property
    def num_str(self) -> str:
        return str(self.num)

    @property
    def subdiv_disp(self) -> str:
        type_ = self.subdiv_type == "article" and "art." or self.subdiv_type
        text = f"{self.subdiv_pos} {type_} {self.subdiv_num} {self.subdiv_mult}"
        return text.strip().capitalize()

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

    ABANDONNED = ("retiré", "irrecevable", "tombé")

    @staticmethod
    def parse_num(text: str) -> Tuple[int, int]:
        if text == "":
            return 0, 0
        if text.startswith("COM-"):
            start = len("COM-")
            text = text[start:]

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

    @property
    def is_displayable(self) -> bool:
        return (
            bool(self.avis) or self.gouvernemental
        ) and self.sort not in self.ABANDONNED

    def replace(self, changes: dict) -> "Amendement":
        amendement = replace(self, **changes)  # type: Amendement
        return amendement

    def asdict(self) -> dict:
        dict_ = asdict(self)  # type: dict
        return dict_

    def changes(self, other: "Amendement", ignored_fields: Iterable[str] = ()) -> dict:
        field_names = (
            field.name for field in fields(self) if field.name not in ignored_fields
        )
        return {
            field_name: (getattr(self, field_name), getattr(other, field_name))
            for field_name in field_names
            if getattr(self, field_name) != getattr(other, field_name)
        }

    @property
    def lecture_url_key(self) -> str:
        return f"{self.chambre}.{self.session}.{self.num_texte}.{self.organe}"

    @property
    def article_url_key(self) -> str:
        return (
            f"{self.subdiv_type}.{self.subdiv_num}.{self.subdiv_mult}.{self.subdiv_pos}"
        )


class SubDiv(NamedTuple):
    type_: str
    num: str
    mult: str
    pos: str
