import re
from datetime import date, datetime
from typing import (
    TYPE_CHECKING,
    Dict,
    Iterable,
    List,
    NamedTuple,
    Optional,
    Tuple,
    Union,
)

from jinja2.filters import do_striptags
from sqlalchemy import (
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import backref, relationship

from zam_repondeur.constants import GROUPS_COLORS
from zam_repondeur.decorator import reify
from zam_repondeur.services.amendements import repository as amendements_repository

from .base import Base, DBSession
from .batch import Batch
from .division import ADJECTIFS_MULTIPLICATIFS

# Make these types available to mypy, but avoid circular imports
if TYPE_CHECKING:
    from .article import Article  # noqa
    from .lecture import Lecture  # noqa
    from .table import SharedTable, UserTable  # noqa


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


GroupingKey = Tuple[str, str, str, str]


class ReponseTuple(NamedTuple):
    avis: str
    objet: str
    content: str
    comments: str

    @property
    def is_empty(self) -> bool:
        return (
            self.avis == ""
            and self.objet == ""
            and self.content == ""
            and self.comments == ""
        )


class AmendementUserContent(Base):
    __tablename__ = "amendement_user_contents"
    __table_args__ = (
        Index(
            "ix_amendement_user_contents__amendement_pk", "amendement_pk", unique=True
        ),
    )

    pk: int = Column(Integer, primary_key=True)
    avis: Optional[str] = Column(Text, nullable=True)
    objet: Optional[str] = Column(Text, nullable=True)
    reponse: Optional[str] = Column(Text, nullable=True)
    comments: Optional[str] = Column(Text, nullable=True)

    amendement_pk: int = Column(
        Integer, ForeignKey("amendements.pk", ondelete="cascade"), nullable=False
    )
    amendement: "Amendement" = relationship("Amendement", back_populates="user_content")

    __repr_keys__ = ("pk", "amendement_pk", "avis")

    @property
    def is_redactionnel(self) -> bool:
        return (
            self.avis == "Favorable"
            and self.objet is not None
            and "rédactionnel" in self.objet.lower()
            and not self.has_reponse
        )

    @property
    def has_objet(self) -> bool:
        return (
            self.objet is not None
            and self.objet.strip() != ""
            and self.objet != "<p></p>"
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

    def similaire(self, other: "AmendementUserContent") -> bool:
        """
        Same answer (with maybe some markup differences)
        """
        return (
            self.avis == other.avis
            and do_striptags(self.objet) == do_striptags(other.objet)  # type: ignore
            and do_striptags(self.reponse)  # type: ignore
            == do_striptags(other.reponse)  # type: ignore
        )

    def as_tuple(self) -> ReponseTuple:
        return ReponseTuple(
            avis=self.avis or "",
            objet=(self.objet.strip() if self.objet else ""),
            content=(self.reponse.strip() if self.reponse else ""),
            comments=(self.comments.strip() if self.comments else ""),
        )


class AmendementLocation(Base):
    __tablename__ = "amendement_location"
    __table_args__ = (
        Index("ix_amendement_location__amendement_pk", "amendement_pk", unique=True),
    )

    pk: int = Column(Integer, primary_key=True)
    amendement_pk: int = Column(
        Integer, ForeignKey("amendements.pk", ondelete="cascade"), nullable=False
    )
    amendement: "Amendement" = relationship("Amendement", back_populates="location")

    user_table_pk: int = Column(Integer, ForeignKey("user_tables.pk"), nullable=True)
    user_table: "Optional[UserTable]" = relationship(
        "UserTable", back_populates="amendements_locations"
    )
    shared_table_pk: int = Column(
        Integer, ForeignKey("shared_tables.pk"), nullable=True
    )
    shared_table: "Optional[SharedTable]" = relationship(
        "SharedTable", back_populates="amendements_locations"
    )
    batch_pk: int = Column(Integer, ForeignKey("batches.pk"), nullable=True)
    batch: Optional[Batch] = relationship(Batch, back_populates="amendements_locations")

    __repr_keys__ = ("pk", "amendement_pk")


class Amendement(Base):
    VERY_BIG_NUMBER = 999_999_999
    __tablename__ = "amendements"
    __table_args__ = (
        Index("ix_amendements__lecture_pk", "lecture_pk"),
        Index("ix_amendements__parent_pk", "parent_pk"),
        UniqueConstraint("num", "lecture_pk"),
        UniqueConstraint("position", "lecture_pk"),
    )

    pk: int = Column(Integer, primary_key=True)
    created_at: datetime = Column(DateTime, nullable=False)

    # Meta informations.
    num: int = Column(Integer, nullable=False)
    rectif: int = Column(Integer, nullable=False, default=0)
    auteur: Optional[str] = Column(Text, nullable=True)
    matricule: Optional[str] = Column(Text, nullable=True)
    groupe: Optional[str] = Column(Text, nullable=True)
    date_depot: Optional[date] = Column(Date, nullable=True)
    sort: Optional[str] = Column(Text, nullable=True)
    mission_titre: Optional[str] = Column(Text, nullable=True)
    mission_titre_court: Optional[str] = Column(Text, nullable=True)

    # Ordre et regroupement lors de la discussion.
    position: Optional[int] = Column(Integer, nullable=True)
    id_discussion_commune: Optional[int] = Column(Integer, nullable=True)
    id_identique: Optional[int] = Column(Integer, nullable=True)

    # Contenu.
    expose: Optional[str] = Column(Text, nullable=True)  # exposé sommaire
    corps: Optional[str] = Column(Text, nullable=True)  # alias dispositif (légistique)
    resume: Optional[str] = Column(Text, nullable=True)  # résumé du corps
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

    lecture_pk: int = Column(Integer, ForeignKey("lectures.pk", ondelete="cascade"))
    lecture: "Lecture" = relationship("Lecture", back_populates="amendements")

    article_pk: int = Column(Integer, ForeignKey("articles.pk"))
    article: "Article" = relationship("Article", back_populates="amendements")

    location: AmendementLocation = relationship(  # technically it's Optional
        AmendementLocation,
        back_populates="amendement",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    user_content: AmendementUserContent = relationship(  # technically it's Optional
        AmendementUserContent,
        back_populates="amendement",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    events = relationship(
        "Event",
        order_by="Event.created_at.desc()",
        cascade="all, delete-orphan",
        passive_deletes=True,
        backref="amendement",
    )

    __repr_keys__ = ("pk", "num", "rectif", "lecture_pk", "article_pk", "parent_pk")

    @classmethod
    def get(cls, lecture: "Lecture", num: int) -> "Amendement":
        amendement: "Amendement" = DBSession.query(cls).filter_by(
            lecture=lecture, num=num
        ).one()
        return amendement

    @classmethod
    def create(  # type: ignore
        cls,
        lecture,
        article,
        num: int,
        rectif: int = 0,
        auteur: str = "",
        groupe: str = "",
        matricule: Optional[str] = None,
        date_depot: Optional[date] = None,
        sort: Optional[str] = None,
        position: Optional[int] = None,
        id_discussion_commune: Optional[int] = None,
        id_identique: Optional[int] = None,
        expose: Optional[str] = None,
        corps: Optional[str] = None,
        resume: Optional[str] = None,
        alinea: Optional[str] = None,
        parent: Optional["Amendement"] = None,
        batch: Optional[Batch] = None,
        mission_titre: Optional[str] = None,
        mission_titre_court: Optional[str] = None,
        avis: Optional[str] = None,
        objet: Optional[str] = None,
        reponse: Optional[str] = None,
        comments: Optional[str] = None,
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
            id_discussion_commune=id_discussion_commune,
            id_identique=id_identique,
            expose=expose,
            corps=corps,
            resume=resume,
            alinea=alinea,
            parent=parent,
            mission_titre=mission_titre,
            mission_titre_court=mission_titre_court,
            created_at=now,
        )
        location = AmendementLocation(amendement=amendement, batch=batch)
        user_content = AmendementUserContent(
            amendement=amendement,
            avis=avis,
            objet=objet,
            reponse=reponse,
            comments=comments,
        )
        DBSession.add(location)
        DBSession.add(user_content)
        return amendement

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Amendement):
            return NotImplemented
        return self.sort_key < other.sort_key

    @property
    def sort_key(self) -> Tuple[bool, int, "Article", int]:
        return (
            self.is_abandoned,
            self.position or self.VERY_BIG_NUMBER,
            self.article,
            self.num,
        )

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
        11: "undecies",
        12: "duodecies",
        13: "terdecies",
        14: "quaterdecies",
        15: "quindecies",
        16: "sexdecies",
        17: "septdecies",
        18: "octodecies",
        19: "novodecies",
        20: "vicies",
        21: "unvicies",
        22: "duovicies",
        23: "tervicies",
        24: "quatervicies",
        25: "quinvicies",
        26: "sexvicies",
        27: "septvicies",
        28: "duodetrecies",
        29: "undetricies",
        30: "tricies",
    }

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
                if suffix in ADJECTIFS_MULTIPLICATIFS:
                    rectif = ADJECTIFS_MULTIPLICATIFS[suffix]
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

    @property
    def is_irrecevable(self) -> bool:
        if not self.sort:
            return False
        return "irrecevable" in self.sort.lower()

    @reify
    def is_abandoned_before_seance(self) -> bool:
        if not self.sort:
            return False
        return self.is_irrecevable or self.is_withdrawn

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
        return (
            bool(self.user_content.avis) or self.gouvernemental
        ) and not self.is_abandoned

    @property
    def is_sous_amendement(self) -> bool:
        return self.parent_pk is not None

    @property
    def identique(self) -> bool:
        return self.id_identique is not None

    @property
    def all_identiques(self) -> List["Amendement"]:
        if self.id_identique is None:
            return []
        return sorted(
            amendement
            for amendement in self.lecture.amendements
            if (
                amendement.id_identique == self.id_identique
                and amendement.article is self.article
                and amendement.num != self.num
                and not amendement.is_abandoned
            )
        )

    @property
    def first_identique_num(self) -> Optional[int]:
        if self.id_identique is None:
            return None
        amdt: Amendement = sorted(
            amendement
            for amendement in self.lecture.amendements
            if amendement.id_identique == self.id_identique
            and amendement.article is self.article
        )[0]
        return amdt.num

    @property
    def displayable_identiques(self) -> List["Amendement"]:
        return [
            amendement
            for amendement in self.all_identiques
            if amendement.is_displayable
            and (
                amendement not in self.location.batch.amendements
                if self.location.batch
                else True
            )
        ]

    @property
    def similaires(self) -> List["Amendement"]:
        return sorted(
            amendement
            for amendement in self.lecture.amendements
            if (
                amendement.article is self.article
                and amendement.num != self.num
                and amendement.reponse_similaire(self)
                and amendement.is_displayable
            )
        )

    def reponse_similaire(self, other: "Amendement") -> bool:
        return self.user_content.similaire(other.user_content)

    @property
    def displayable_identiques_are_similaires(self) -> bool:
        return self.displayable_identiques == self.similaires

    def grouped_displayable_children(
        self
    ) -> Iterable[Tuple[GroupingKey, List["Amendement"]]]:
        return self.article.group_amendements(
            amdt for amdt in self.children if amdt.is_displayable
        )

    @property
    def table_name(self) -> str:
        if self.location.shared_table:
            return self.location.shared_table.titre or ""
        elif self.location.user_table:
            return (
                self.location.user_table.user.name
                or self.location.user_table.user.email
            )
        else:
            return ""

    @property
    def is_being_edited(self) -> bool:
        return bool(amendements_repository.get_last_activity_time(self.pk))

    def start_editing(self) -> None:
        if not self.location.user_table:
            return
        amendements_repository.start_editing(self.pk, self.location.user_table.user.pk)

    def stop_editing(self) -> None:
        amendements_repository.stop_editing(self.pk)

    def asdict(self) -> dict:
        result: Dict[str, Union[str, int, date]] = {
            "num": self.num,
            "rectif": self.rectif or "",
            "sort": self.sort or "",
            "matricule": self.matricule or "",
            "gouvernemental": self.gouvernemental,
            "auteur": self.auteur or "",
            "groupe": self.groupe or "",
            "expose": self.expose or "",
            "corps": self.corps or "",
            "resume": self.resume or "",
            "objet": self.user_content.objet or "",
            "avis": self.user_content.avis or "",
            "reponse": self.user_content.reponse or "",
            "comments": self.user_content.comments or "",
            "parent": self.parent and self.parent.num_disp or "",
            "chambre": str(self.lecture.chambre),
            "num_texte": self.lecture.texte.numero,
            "organe": self.lecture.organe,
            "legislature": self.lecture.texte.legislature or "",
            "session": self.lecture.texte.session_str or "",
            "article": self.article.format(),
            "article_titre": self.article.user_content.title or "",
            "article_order": self.article.sort_key_as_str,
            "position": self.position or "",
            "id_discussion_commune": self.id_discussion_commune or "",
            "id_identique": self.id_identique or "",
            "first_identique_num": self.first_identique_num or "",
            "alinea": self.alinea or "",
            "date_depot": self.date_depot or "",
            "affectation_email": self.location.user_table
            and self.location.user_table.user.email
            or "",
            "affectation_name": self.location.user_table
            and self.location.user_table.user.name
            or "",
        }
        return result
