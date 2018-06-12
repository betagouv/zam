from sqlalchemy import Boolean, Column, Date, Integer, Text
from sqlalchemy.schema import ForeignKeyConstraint

from zam_aspirateur.amendements.models import Amendement as AmendementData

from .base import Base


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


class Amendement(Base):  # type: ignore

    __tablename__ = "amendements"

    __table_args__ = (
        ForeignKeyConstraint(
            ["chambre", "session", "num_texte"],
            ["lectures.chambre", "lectures.session", "lectures.num_texte"],
        ),
    )

    # Identification du texte
    chambre = Column(Text, primary_key=True, nullable=False)
    session = Column(Text, primary_key=True, nullable=False)
    num_texte = Column(Text, primary_key=True, nullable=False)

    # Partie du texte visée
    subdiv_type = Column(Text, nullable=False)  # article, ...
    subdiv_num = Column(Text, nullable=False)  # numéro
    subdiv_mult = Column(Text, nullable=True)  # bis, ter...
    subdiv_pos = Column(Text, nullable=True)  # avant / après
    alinea = Column(Text, nullable=True)  # libellé de l'alinéa de l'article concerné

    # Numéro de l'amendement
    num = Column(Integer, primary_key=True, nullable=True)

    # Numéro de révision de l'amendement
    rectif = Column(Integer, nullable=False, default=0)

    # Auteur de l'amendement
    auteur = Column(Text, nullable=True)
    matricule = Column(Text, nullable=True)
    groupe = Column(Text, nullable=True)  # groupe parlementaire

    # Date de dépôt de l'amendement (est-ce la date initiale,
    # ou bien est-ce mis à jour si l'amendement est rectifié ?)
    date_depot = Column(Date, nullable=True)

    sort = Column(Text, nullable=True)  # retiré, adopté, etc.

    # Ordre et regroupement lors de la discussion
    position = Column(Integer, nullable=True)
    discussion_commune = Column(Integer, nullable=True)
    identique = Column(Boolean, nullable=True)

    dispositif = Column(Text, nullable=True)  # texte de l'amendement
    objet = Column(Text, nullable=True)  # motivation

    resume = Column(Text, nullable=True)  # résumé de l'objet

    avis = Column(Text, nullable=True)  # position du gouvernemnt
    observations = Column(Text, nullable=True)
    reponse = Column(Text, nullable=True)

    @classmethod
    def from_dataclass(
        cls,
        data: AmendementData,
        chambre: str,
        session: str,
        num_texte: str,
        position: int,
    ) -> "Amendement":
        attrs = data.asdict()
        attrs.pop("num")
        attrs.pop("rectif")
        return cls(
            chambre=chambre,
            session=session,
            num_texte=num_texte,
            position=position,
            num=data.num_int,
            rectif=0 if data.rectif == "" else int(data.rectif),
            **attrs,
        )

    @property
    def gouvernemental(self) -> bool:
        return str(self.auteur) == "LE GOUVERNEMENT"

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
