from typing import Iterable

from sqlalchemy import Column, ForeignKey, Integer, PickleType, Text
from sqlalchemy.orm import relationship, validates

from .base import Base, DBSession
from .lecture import Lecture


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
    type = Column(Text, nullable=True)  # article, ...
    num = Column(Text, nullable=True)  # numéro
    mult = Column(Text, nullable=True)  # bis, ter...
    pos = Column(Text, nullable=True)  # avant / après
    titre = Column(Text, nullable=True)
    contenu = Column(PickleType, nullable=True)
    jaune = Column(Text, nullable=True)  # éléments de langage

    amendements = relationship("Amendement", back_populates="article")

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
        type_ = self.type == "article" and "art." or self.type
        text = f"{self.pos} {type_} {self.num} {self.mult}"
        return text.strip().capitalize()

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
