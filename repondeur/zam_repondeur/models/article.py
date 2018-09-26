import logging
from itertools import groupby
from typing import Iterable, List, Optional, Tuple, Union

from sqlalchemy import Column, ForeignKey, Integer, PickleType, Text
from sqlalchemy.orm import relationship, validates

from .base import Base, DBSession
from .amendement import Amendement
from .lecture import Lecture


logger = logging.getLogger(__name__)


AVIS = [
    "Favorable",
    "Défavorable",
    "Favorable sous réserve de",
    "Retrait",
    "Retrait au profit de",
    "Retrait sinon rejet",
    "Retrait sous réserve de",
    "Sagesse",
]


ALLOWED_TYPE = (
    "",
    "titre",
    "motion",
    "chapitre",
    "section",
    "sous-section",
    "article",
    "annexe",
)

ALLOWED_MULT = (
    "",
    "bis",
    "ter",
    "quater",
    "quinquies",
    "sexies",
    "septies",
    "octies",
    "nonies",
    "decies",
)

ALLOWED_POS = ("avant", "", "après")


class Article(Base):
    __tablename__ = "articles"

    pk = Column(Integer, primary_key=True)
    lecture_pk = Column(Integer, ForeignKey("lectures.pk"), nullable=False)
    lecture = relationship(Lecture, back_populates="articles")
    type = Column(Text, nullable=True)  # type: Optional[str]
    num = Column(Text, nullable=True)  # type: Optional[str]
    mult = Column(Text, nullable=True)  # type: Optional[str]
    pos = Column(Text, nullable=True)  # type: Optional[str]
    titre = Column(Text, nullable=True)
    contenu = Column(PickleType, nullable=True)
    jaune = Column(Text, nullable=True)  # éléments de langage

    amendements = relationship(
        Amendement,
        order_by=(Amendement.position, Amendement.num),
        back_populates="article",
    )

    @validates("type")
    def validate_type(self, key: str, type: str) -> str:
        return validate(key, type, ALLOWED_TYPE)

    @validates("mult")
    def validate_mult(self, key: str, mult: str) -> str:
        return validate(key, mult, ALLOWED_MULT)

    @validates("pos")
    def validate_pos(self, key: str, pos: str) -> str:
        return validate(key, pos, ALLOWED_POS)

    __repr_keys__ = ("pk", "lecture_pk", "type", "num", "mult", "pos")

    def __str__(self) -> str:
        if self.type == "annexe" and not self.num:
            return "Annexes"
        type_ = "art." if self.type == "article" else self.type or ""
        text = f"{self.pos} {type_} {self.num} {self.mult}"
        return text.strip().capitalize()

    def format(self, short: bool = False) -> str:
        if self.type == "annexe" and not self.num:
            return "Annexes"
        type_ = "art." if self.type == "article" and short else self.type or ""
        if self.pos:
            type_ += f" add. {self.pos[:2]}."
        text = f"{type_} {self.num} {self.mult}"
        return text.strip().capitalize()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Article):
            return NotImplemented
        if self.lecture != other.lecture:
            raise ValueError
        return bool(
            (self.type == other.type)
            and (self.num == other.num)
            and (self.mult == other.mult)
            and (self.pos == other.pos)
        )

    _ORDER_TYPE = {
        "titre": 1,
        "motion": 2,
        "chapitre": 3,
        "section": 4,
        "sous-section": 5,
        "article": 6,
        "annexe": 7,
        "": 8,
    }

    _ORDER_MULT = {
        "": 1,
        "bis": 2,
        "ter": 3,
        "quater": 4,
        "quinquies": 5,
        "sexies": 6,
        "septies": 7,
        "octies": 8,
        "nonies": 9,
        "decies": 10,
    }

    _ORDER_POS = {"avant": 0, "": 1, "apres": 2, "après": 2}

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Article):
            return NotImplemented
        if self.lecture != other.lecture:
            raise ValueError
        return self.sort_key < other.sort_key

    @property
    def sort_key(self) -> Tuple[int, Union[int, str], int, int]:
        def maybe_int(value: Optional[str]) -> Union[int, str]:
            if value is None:
                return 0
            try:
                return int(value)
            except ValueError:
                return value

        return (
            Article._ORDER_TYPE[self.type or ""],
            maybe_int(self.num),
            Article._ORDER_MULT[self.mult or ""],
            Article._ORDER_POS[self.pos or ""],
        )

    @classmethod
    def create(
        cls,
        lecture: Lecture,
        type: str,
        num: str = "",
        mult: str = "",
        pos: str = "",
        titre: str = "",
        contenu: dict = {},
        jaune: str = "",
    ) -> "Article":
        article = cls(
            lecture=lecture,
            type=type,
            num=num,
            mult=mult,
            pos=pos,
            titre=titre,
            contenu=contenu,
            jaune=jaune,
        )
        DBSession.add(article)
        return article

    @property
    def slug(self) -> str:
        parts = []
        if self.type:
            parts.append(self.type)
        if self.pos:
            parts.extend(["add", self.pos[:2].lower()])
        parts.append(str(self.num))
        if self.mult:
            parts.append(self.mult)
        return "-".join(parts)

    @property
    def url_key(self) -> str:
        return f"{self.type}.{self.num}.{self.mult}.{self.pos}"

    def grouped_displayable_amendements(self) -> Iterable[List[Amendement]]:
        displayable_amendements = (
            amdt for amdt in self.amendements if amdt.is_displayable
        )
        return (
            list(amendements)
            for _, amendements in groupby(
                displayable_amendements, key=Amendement.grouping_key
            )
        )


def validate(name: str, value: str, allowed: Iterable[str]) -> str:
    if not isinstance(value, str):
        raise ValueError(f"Invalid type '{type(value)}' for {name} (expected str)")
    if value not in allowed:
        raise ValueError(
            f"Invalid value '{value}' for {name} (allowed: {format_list(allowed)})"
        )
    return value


def format_list(items: Iterable[str]) -> str:
    return ", ".join(f"'{item}'" for item in items)