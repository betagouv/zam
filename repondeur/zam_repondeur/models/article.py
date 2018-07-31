from sqlalchemy import Column, Integer, PickleType, Text
from sqlalchemy.orm import relationship

from .base import Base, DBSession


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


class Article(Base):  # type: ignore
    __tablename__ = "articles"

    pk = Column(Integer, primary_key=True)
    type = Column(Text)  # article, ...
    num = Column(Text, nullable=True)  # numéro
    mult = Column(Text, nullable=True)  # bis, ter...
    pos = Column(Text, nullable=True)  # avant / après
    titre = Column(Text, nullable=True)
    contenu = Column(PickleType, nullable=True)
    jaune = Column(Text, nullable=True)  # éléments de langage

    amendements = relationship("Amendement", back_populates="article")

    def __str__(self) -> str:
        type_ = self.type == "article" and "art." or self.type
        text = f"{self.pos} {type_} {self.num} {self.mult}"
        return text.strip().capitalize()

    @classmethod
    def create(
        cls,
        type: str,
        num: str = "",
        mult: str = "",
        pos: str = "",
        titre: str = "",
        contenu: dict = {},
        jaune: str = "",
    ) -> "Article":
        article = cls(
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
