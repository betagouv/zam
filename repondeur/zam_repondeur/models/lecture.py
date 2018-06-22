from typing import Any, List

from sqlalchemy import Column, Integer, Text, desc

from .base import Base, DBSession


CHAMBRES = {"an": "Assemblée nationale", "senat": "Sénat"}

SESSIONS = {
    "an": {"15": "15e législature", "14": "14e législature"},
    "senat": {"2017-2018": "2017-2018"},
}


class Lecture(Base):  # type: ignore
    __tablename__ = "lectures"

    chambre = Column(Text, primary_key=True)
    session = Column(Text, primary_key=True)
    num_texte = Column(Integer, primary_key=True)
    titre = Column(Text)

    @property
    def chambre_disp(self) -> str:
        return CHAMBRES[self.chambre]

    def __str__(self) -> str:
        return f"{self.chambre_disp}, session {self.session}, texte nº {self.num_texte}"

    def __lt__(self, other: Any) -> bool:
        if type(self) != type(other):
            return NotImplemented
        return (self.chambre, self.session, self.num_texte) < (
            other.chambre,
            other.session,
            other.num_texte,
        )

    @classmethod
    def all(cls) -> List["Lecture"]:
        lectures: List["Lecture"] = DBSession.query(cls).order_by(
            cls.chambre, desc(cls.session), desc(cls.num_texte)
        ).all()
        return lectures

    @classmethod
    def get(cls, chambre: str, session: str, num_texte: int) -> "Lecture":
        res: "Lecture" = (
            DBSession.query(cls)
            .filter(
                cls.chambre == chambre,
                cls.session == session,
                cls.num_texte == num_texte,
            )
            .first()
        )
        return res

    @classmethod
    def exists(cls, chambre: str, session: str, num_texte: int) -> bool:
        res: bool = DBSession.query(
            DBSession.query(cls)
            .filter(
                cls.chambre == chambre,
                cls.session == session,
                cls.num_texte == num_texte,
            )
            .exists()
        ).scalar()
        return res

    @classmethod
    def create(
        cls, chambre: str, session: str, num_texte: int, titre: str
    ) -> "Lecture":
        lecture = cls(
            chambre=chambre, session=session, num_texte=num_texte, titre=titre
        )
        DBSession.add(lecture)
        return lecture
