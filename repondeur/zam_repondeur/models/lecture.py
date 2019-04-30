from datetime import datetime
from typing import Any, List, Optional, Tuple, TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, Text, desc
from sqlalchemy.orm import joinedload, relationship

from .amendement import Amendement
from .article import Article
from .base import Base, DBSession
from .division import SubDiv
from .events.base import LastEventMixin
from .texte import Chambre, Texte
from .users import Team

# Make these types available to mypy, but avoid circular imports
if TYPE_CHECKING:
    from .dossier import Dossier  # noqa


CHAMBRES = {"an": "Assemblée nationale", "senat": "Sénat"}

SESSIONS = {
    "an": {"15": "15e législature", "14": "14e législature"},
    "senat": {"2017-2018": "2017-2018"},
}


class Lecture(Base, LastEventMixin):
    __tablename__ = "lectures"
    __table_args__ = (
        Index(
            "ix_lectures__chambre__session__partie__organe",
            "chambre",
            "session",
            "partie",
            "organe",
            unique=True,
        ),
    )

    pk = Column(Integer, primary_key=True)
    chambre = Column(Text)
    session = Column(Text)
    partie = Column(Integer, nullable=True)  # only for PLF
    organe = Column(Text)
    titre = Column(Text)
    created_at: datetime = Column(DateTime)
    modified_at = Column(DateTime)
    amendements = relationship(
        Amendement,
        order_by=(Amendement.position, Amendement.num),
        back_populates="lecture",
        cascade="all, delete-orphan",
    )
    articles = relationship(
        Article, back_populates="lecture", cascade="all, delete-orphan"
    )

    owned_by_team_pk = Column(Integer, ForeignKey("teams.pk"), nullable=True)
    owned_by_team = relationship("Team", backref="lectures")
    dossier_pk = Column(Integer, ForeignKey("dossiers.pk"))
    dossier = relationship("Dossier", back_populates="lectures")
    texte_pk = Column(Integer, ForeignKey("textes.pk"))
    texte = relationship(Texte, back_populates="lectures")

    __repr_keys__ = ("pk", "chambre", "session", "organe", "partie", "owned_by_team")

    def __str__(self) -> str:
        return ", ".join(
            [
                self.format_chambre(),
                self.format_session(),
                self.format_organe(),
                self.format_num_lecture(),
                self.format_texte(),
            ]
        )

    def format_chambre(self) -> str:
        return CHAMBRES[self.chambre]

    def format_session(self) -> str:
        if self.chambre == "an":
            return f"{self.session}e législature"
        else:
            return f"session {self.session}"

    def format_organe(self) -> str:
        from zam_repondeur.data import repository  # avoid circular imports

        result: str = self.organe
        organes = repository.get_data("organes")
        if self.organe in organes:
            organe_data = organes[self.organe]
            result = organe_data["libelleAbrege"]
        return self.rewrite_organe(result)

    def rewrite_organe(self, label: str) -> str:
        if label in {"Assemblée", "Sénat"}:
            return "Séance publique"
        if label.startswith("Commission"):
            return label
        return f"Commission des {label.lower()}"

    def format_num_lecture(self) -> str:
        num_lecture, title = self.titre.split(" – ", 1)
        return str(num_lecture.strip())

    def format_texte(self) -> str:
        if self.partie == 1:
            partie = " (1re partie)"
        elif self.partie == 2:
            partie = " (2nde partie)"
        else:
            partie = ""
        return f"texte nº\u00a0{self.texte.numero}{partie}"

    def __lt__(self, other: Any) -> bool:
        if type(self) != type(other):
            return NotImplemented
        return (self.chambre, self.session, self.texte.numero, self.organe) < (
            other.chambre,
            other.session,
            other.texte.numero,
            other.organe,
        )

    @property
    def modified_at_timestamp(self) -> float:
        timestamp: float = (self.modified_at - datetime(1970, 1, 1)).total_seconds()
        return timestamp

    @property
    def modified_amendements_at_timestamp(self) -> float:
        if not self.amendements:
            return 0
        max_modified_at: float = max(
            amendement.modified_at_timestamp for amendement in self.amendements
        )
        return max_modified_at

    def modified_amendements_numbers_since(self, timestamp: float) -> List[str]:
        if not self.amendements:
            return []
        return [
            str(amendement)
            for amendement in self.amendements
            if amendement.modified_at_timestamp > timestamp
        ]

    @property
    def displayable(self) -> bool:
        return any(amd.is_displayable for amd in self.amendements)

    @classmethod
    def all(cls) -> List["Lecture"]:
        lectures: List["Lecture"] = (
            DBSession.query(cls)
            .options(joinedload("amendements"))
            .order_by(desc(cls.created_at))
            .all()
        )
        return lectures

    @classmethod
    def get(
        cls,
        chambre: str,
        session_or_legislature: str,
        num_texte: int,
        partie: Optional[int],
        organe: str,
        *options: Any,
    ) -> Optional["Lecture"]:
        query = (
            DBSession.query(cls)
            .join(Texte)
            .filter(
                cls.chambre == chambre,
                cls.session == session_or_legislature,
                cls.partie == partie,
                cls.organe == organe,
                Texte.chambre == Chambre.from_string(chambre),
                Texte.numero == num_texte,
            )
            .options(*options)
        )
        if chambre == "an":
            query = query.filter(Texte.legislature == int(session_or_legislature))
        elif chambre == "senat":
            query = query.filter(
                Texte.session == int(session_or_legislature.split("-")[0])
            )
        else:
            raise ValueError("Invalid value for chambre")
        res: Optional["Lecture"] = query.first()
        return res

    @classmethod
    def exists(
        cls,
        chambre: str,
        session: str,
        texte: "Texte",
        partie: Optional[int],
        organe: str,
    ) -> bool:
        res: bool = DBSession.query(
            DBSession.query(cls)
            .filter(
                cls.chambre == chambre,
                cls.session == session,
                cls.texte == texte,
                cls.partie == partie,
                cls.organe == organe,
            )
            .exists()
        ).scalar()
        return res

    @classmethod
    def create(
        cls,
        chambre: str,
        session: str,
        texte: "Texte",
        titre: str,
        organe: str,
        dossier: "Dossier",
        partie: Optional[int] = None,
        owned_by_team: Optional[Team] = None,
    ) -> "Lecture":
        now = datetime.utcnow()
        lecture = cls(
            chambre=chambre,
            session=session,
            texte=texte,
            titre=titre,
            organe=organe,
            dossier=dossier,
            partie=partie,
            owned_by_team=owned_by_team,
            created_at=now,
            modified_at=now,
        )
        DBSession.add(lecture)
        return lecture

    @property
    def url_key(self) -> str:
        if self.partie is not None:
            partie = f"-{self.partie}"
        else:
            partie = ""
        return (
            f"{self.chambre}.{self.session}.{self.texte.numero}{partie}.{self.organe}"
        )

    def find_article(self, subdiv: SubDiv) -> Optional[Article]:
        article: Article
        for article in self.articles:
            if article.matches(subdiv):
                return article
        return None

    def find_or_create_article(self, subdiv: SubDiv) -> Tuple[Article, bool]:
        article = self.find_article(subdiv)
        created = False
        if article is None:
            article = Article.create(
                lecture=self,
                type=subdiv.type_,
                num=subdiv.num,
                mult=subdiv.mult,
                pos=subdiv.pos,
            )
            created = True
        return article, created

    def find_amendement(self, num: int) -> Optional[Amendement]:
        amendement: Amendement
        for amendement in self.amendements:
            if amendement.num == num:
                return amendement
        return None

    def find_or_create_amendement(
        self, num: int, article: Article
    ) -> Tuple[Amendement, bool]:
        amendement = self.find_amendement(num)
        created = False
        if amendement is None:
            amendement = Amendement.create(lecture=self, article=article, num=num)
            created = True
        return amendement, created
