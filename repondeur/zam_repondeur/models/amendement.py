import re
from datetime import date, datetime
from typing import (
    Dict,
    Iterable,
    List,
    NamedTuple,
    Optional,
    Tuple,
    Union,
    TYPE_CHECKING,
)  # noqa

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import backref, relationship

from zam_repondeur.constants import GROUPS_COLORS
from zam_repondeur.decorator import reify

from .base import Base, DBSession


# Make these types available to mypy, but avoid circular imports
if TYPE_CHECKING:
    from .article import Article  # noqa
    from .lecture import Lecture  # noqa


AVIS = [
    "Favorable",
    "Défavorable",
    "Favorable sous réserve de",
    "Retrait",
    "Retrait au profit de",
    "Retrait sinon rejet",
    "Retrait sous réserve de",
    "Sagesse",
    "Satisfait donc rejet",
]


class Reponse(NamedTuple):
    avis: str
    observations: str
    content: str


class Amendement(Base):
    VERY_BIG_NUMBER = 999_999_999
    __tablename__ = "amendements"
    __table_args__ = (UniqueConstraint("num", "lecture_pk"),)

    pk: int = Column(Integer, primary_key=True)
    created_at: datetime = Column(DateTime, nullable=False)
    modified_at: datetime = Column(DateTime, nullable=False)

    # Meta informations.
    num: int = Column(Integer, nullable=False)
    rectif: int = Column(Integer, nullable=False, default=0)
    auteur: Optional[str] = Column(Text, nullable=True)
    matricule: Optional[str] = Column(Text, nullable=True)
    groupe: Optional[str] = Column(Text, nullable=True)
    date_depot: Optional[date] = Column(Date, nullable=True)
    sort: Optional[str] = Column(Text, nullable=True)

    # Ordre et regroupement lors de la discussion.
    position: Optional[int] = Column(Integer, nullable=True)
    discussion_commune: Optional[int] = Column(Integer, nullable=True)
    identique: Optional[bool] = Column(Boolean, nullable=True)

    # Contenu.
    dispositif: Optional[str] = Column(Text, nullable=True)  # texte de l'amendement
    objet: Optional[str] = Column(Text, nullable=True)  # motivation
    resume: Optional[str] = Column(Text, nullable=True)  # résumé de l'objet
    alinea: Optional[str] = Column(Text, nullable=True)  # libellé de l'alinéa ciblé

    # Relations.
    parent_pk: Optional[int] = Column(
        Integer, ForeignKey("amendements.pk"), nullable=True
    )
    parent_rectif: Optional[int] = Column(Integer, nullable=True)
    parent: Optional["Amendement"] = relationship(
        "Amendement",
        uselist=False,
        remote_side=[pk],
        backref=backref("children"),
        post_update=True,
    )
    lecture_pk: int = Column(Integer, ForeignKey("lectures.pk"))
    lecture: "Lecture" = relationship("Lecture", back_populates="amendements")
    article_pk: int = Column(Integer, ForeignKey("articles.pk"))
    article: "Article" = relationship("Article", back_populates="amendements")

    # Extras. (TODO: move to dedicated table?)
    avis: Optional[str] = Column(Text, nullable=True)
    observations: Optional[str] = Column(Text, nullable=True)
    reponse: Optional[str] = Column(Text, nullable=True)
    comments: Optional[str] = Column(Text, nullable=True)
    bookmarked_at: Optional[datetime] = Column(DateTime, nullable=True)

    __repr_keys__ = ("pk", "num", "rectif", "lecture_pk", "article_pk", "parent_pk")

    @classmethod
    def create(  # type: ignore
        cls,
        lecture,
        article,
        num: int,
        rectif: int = 0,
        auteur: Optional[str] = None,
        matricule: Optional[str] = None,
        groupe: Optional[str] = None,
        date_depot: Optional[date] = None,
        sort: Optional[str] = None,
        position: Optional[int] = None,
        discussion_commune: Optional[int] = None,
        identique: Optional[bool] = None,
        dispositif: Optional[str] = None,
        objet: Optional[str] = None,
        resume: Optional[str] = None,
        alinea: Optional[str] = None,
        parent: Optional["Amendement"] = None,
        avis: Optional[str] = None,
        observations: Optional[str] = None,
        reponse: Optional[str] = None,
        comments: Optional[str] = None,
        bookmarked_at: Optional[datetime] = None,
    ) -> "Amendement":
        now = datetime.utcnow()
        amendement = cls(
            lecture=lecture,
            article=article,
            num=num,
            rectif=rectif,
            auteur=auteur,
            matricule=matricule,
            groupe=groupe,
            date_depot=date_depot,
            sort=sort,
            position=position,
            discussion_commune=discussion_commune,
            identique=identique,
            dispositif=dispositif,
            objet=objet,
            resume=resume,
            alinea=alinea,
            parent=parent,
            avis=avis,
            observations=observations,
            reponse=reponse,
            comments=comments,
            bookmarked_at=bookmarked_at,
            created_at=now,
            modified_at=now,
        )
        DBSession.add(amendement)
        return amendement

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Amendement):
            return NotImplemented
        return self.sort_key < other.sort_key

    @property
    def modified_at_timestamp(self) -> float:
        timestamp: float = (self.modified_at - datetime(1970, 1, 1)).total_seconds()
        return timestamp

    @property
    def sort_key(self) -> Tuple[bool, int, int]:
        return (self.is_abandoned, self.position or self.VERY_BIG_NUMBER, self.num)

    @reify
    def num_str(self) -> str:
        return str(self.num)

    @reify
    def num_disp(self) -> str:
        text = self.num_str
        if self.rectif > 0:
            text += " rect."
        if self.rectif > 1:
            if self.rectif not in self._RECTIF_TO_SUFFIX:
                raise NotImplementedError
            text += " "
            text += self._RECTIF_TO_SUFFIX[self.rectif]
        return text

    def __str__(self) -> str:
        return self.num_disp

    @property
    def couleur_groupe(self) -> str:
        return GROUPS_COLORS.get(self.groupe or "", "#ffffff")

    @property
    def slug(self) -> str:
        return f'amdt-{self.num_disp.replace(" ", "-").replace(".", "")}'

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

    _NUM_RE = re.compile(
        r"""
            (?P<prefix>[A-Z\|\-]*)
            (?P<num>\d+)
            (?P<rect>\ rect\.(?:\ (?P<suffix>\w+))?)?
        """,
        re.VERBOSE,
    )

    @staticmethod
    def parse_num(text: str) -> Tuple[int, int]:
        if text == "":
            return 0, 0

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

    @reify
    def gouvernemental(self) -> bool:
        return self.auteur == "LE GOUVERNEMENT"

    @property
    def is_withdrawn(self) -> bool:
        if not self.sort:
            return False
        return "retiré" in self.sort.lower()

    @reify
    def is_abandoned_before_seance(self) -> bool:
        if not self.sort:
            return False
        return self.sort.lower() == "irrecevable" or self.is_withdrawn

    @property
    def is_abandoned_during_seance(self) -> bool:
        if not self.sort:
            return False
        return self.sort.lower() == "tombé" or self.is_withdrawn

    @property
    def is_abandoned(self) -> bool:
        return self.is_abandoned_before_seance or self.is_abandoned_during_seance

    @property
    def is_displayable(self) -> bool:
        return (bool(self.avis) or self.gouvernemental) and not self.is_abandoned

    @property
    def is_sous_amendement(self) -> bool:
        return self.parent_pk is not None

    def grouped_displayable_children(
        self
    ) -> Iterable[Tuple[Reponse, List["Amendement"]]]:
        return self.article.group_amendements(
            amdt for amdt in self.children if amdt.is_displayable
        )

    @property
    def is_redactionnel(self) -> bool:
        return (
            self.avis == "Favorable"
            and self.objet is not None
            and "rédactionnel" in self.objet.lower()
            and not self.has_reponse
        )

    @property
    def has_reponse(self) -> bool:
        return (
            self.reponse is not None
            and self.reponse.strip() != ""
            and self.reponse != "<p></p>"
        )

    @property
    def favorable(self) -> bool:
        if self.avis is None:
            return False
        return self.avis.startswith("Favorable")

    @property
    def sagesse(self) -> bool:
        if self.avis is None:
            return False
        return self.avis == "Sagesse" or self.avis == "Satisfait donc rejet"

    @property
    def lecture_url_key(self) -> str:
        return (
            f"{self.lecture.chambre}.{self.lecture.session}."
            f"{self.lecture.num_texte}.{self.lecture.organe}"
        )

    def grouping_key(self) -> Reponse:
        if self.gouvernemental:
            return Reponse(self.num_str, "", "")
        return Reponse(self.avis or "", self.observations or "", self.reponse or "")

    def asdict(self, full: bool = False) -> dict:
        result: Dict[str, Union[str, int, date]] = {
            "num": self.num,
            "rectif": self.rectif or "",
            "pk": f"{self.num:06}",
            "sort": self.sort or "",
            "matricule": self.matricule or "",
            "gouvernemental": self.gouvernemental,
            "auteur": self.auteur or "",
            "groupe": self.groupe or "",
            "dispositif": self.dispositif or "",
            "objet": self.objet or "",
            "resume": self.resume or "",
            "observations": self.observations or "",
            "avis": self.avis or "",
            "reponse": self.reponse or "",
            "comments": self.comments or "",
            "parent": self.parent and self.parent.num_disp or "",
        }
        if full:
            result["chambre"] = self.lecture.chambre
            result["num_texte"] = self.lecture.num_texte
            result["organe"] = self.lecture.organe
            result["session"] = self.lecture.session
            result["article"] = self.article.format()
            result["article_titre"] = self.article.titre or ""
            result["position"] = self.position or ""
            result["discussion_commune"] = self.discussion_commune or ""
            result["identique"] = self.identique or ""
            result["alinea"] = self.alinea or ""
            result["date_depot"] = self.date_depot or ""
            result["bookmarked_at"] = "Oui" if self.bookmarked_at else "Non"
        return result
