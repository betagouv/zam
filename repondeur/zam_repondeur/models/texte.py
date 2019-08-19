import enum
from datetime import date, datetime
from typing import Any, Optional, cast

from sqlalchemy import Column, Date, DateTime, Enum, Index, Integer
from sqlalchemy.orm import relationship

from .base import Base, DBSession
from .chambre import Chambre


class TypeTexte(enum.Enum):
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


class Texte(Base):
    __tablename__ = "textes"
    __table_args__ = (
        Index(
            "uq_textes_chambre_session_legislature_numero_key",
            "chambre",
            "session",
            "legislature",
            "numero",
            unique=True,
        ),
    )

    pk = Column(Integer, primary_key=True)

    type_ = Column(Enum(TypeTexte), nullable=False)
    chambre = Column(Enum(Chambre), nullable=False)

    # Sénat only: starting year of the session (e.g. 2018 for 2018-2019)
    session = Column(Integer, nullable=True)

    # Assemblée Nationale only
    legislature = Column(Integer, nullable=True)

    numero = Column(Integer, nullable=False)
    date_depot = Column(Date, nullable=False)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    modified_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    lectures = relationship("Lecture", back_populates="texte")

    __repr_keys__ = (
        "pk",
        "type_",
        "chambre",
        "numero",
        "session",
        "legislature",
        "date_depot",
    )

    @property
    def session_str(self) -> Optional[str]:
        if self.session is None:
            return None
        return f"{self.session}-{self.session + 1}"

    @classmethod
    def get(
        cls, chambre: Chambre, session_or_legislature: str, numero: int
    ) -> Optional["Texte"]:
        query = DBSession.query(cls).filter(
            cls.chambre == chambre, cls.numero == numero
        )
        if chambre == Chambre.AN:
            query = query.filter_by(legislature=int(session_or_legislature))
        else:
            query = query.filter_by(session=int(session_or_legislature.split("-")[0]))
        res: Optional["Texte"] = query.first()
        return res

    @classmethod
    def create(
        cls,
        type_: TypeTexte,
        chambre: Chambre,
        numero: int,
        date_depot: date,
        session: Optional[int] = None,
        legislature: Optional[int] = None,
    ) -> "Texte":
        now = datetime.utcnow()
        if chambre == Chambre.AN and legislature is None:
            raise ValueError("legislature is required for AN")
        if chambre == Chambre.SENAT and session is None:
            raise ValueError("session is required for SENAT")
        texte = cls(
            type_=type_,
            chambre=chambre,
            numero=numero,
            date_depot=date_depot,
            session=session,
            legislature=legislature,
            created_at=now,
            modified_at=now,
        )
        DBSession.add(texte)
        return texte

    @classmethod
    def get_or_create_from_ref(cls, texte_ref: Any, chambre: Chambre) -> "Texte":
        from zam_repondeur.models import get_one_or_create  # Circular.

        if texte_ref.date_depot is None:
            raise RuntimeError("Cannot create LectureRef for Texte with no date_depot")

        texte, _ = get_one_or_create(
            Texte,
            type_=texte_ref.type_,
            chambre=chambre,
            legislature=texte_ref.legislature,
            session=texte_ref.session,
            numero=texte_ref.numero,
            date_depot=texte_ref.date_depot,
        )
        return cast(Texte, texte)
