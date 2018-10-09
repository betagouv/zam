import re
from typing import Optional, Tuple  # noqa

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

VERY_BIG_NUMBER = 999_999_999


class Amendement(Base):
    __tablename__ = "amendements"
    __table_args__ = (UniqueConstraint("num", "lecture_pk"),)

    pk = Column(Integer, primary_key=True)

    # Meta informations.
    num = Column(Integer, nullable=False)  # type: int
    rectif = Column(Integer, nullable=False, default=0)
    auteur = Column(Text, nullable=True)  # type: Optional[str]
    matricule = Column(Text, nullable=True)
    groupe = Column(Text, nullable=True)
    date_depot = Column(Date, nullable=True)
    sort = Column(Text, nullable=True)

    # Ordre et regroupement lors de la discussion.
    position = Column(Integer, nullable=True)  # type: Optional[int]
    discussion_commune = Column(Integer, nullable=True)
    identique = Column(Boolean, nullable=True)

    # Contenu.
    dispositif = Column(Text, nullable=True)  # texte de l'amendement
    objet = Column(Text, nullable=True)  # motivation
    resume = Column(Text, nullable=True)  # résumé de l'objet
    alinea = Column(Text, nullable=True)  # libellé de l'alinéa de l'article concerné

    # Relations.
    parent_pk = Column(Integer, ForeignKey("amendements.pk"), nullable=True)
    parent_rectif = Column(Integer, nullable=True)
    parent = relationship(
        "Amendement",
        uselist=False,
        remote_side=[pk],
        backref=backref("children"),
        post_update=True,
    )
    lecture_pk = Column(Integer, ForeignKey("lectures.pk"))
    lecture = relationship("Lecture", back_populates="amendements")
    article_pk = Column(Integer, ForeignKey("articles.pk"))
    article = relationship("Article", back_populates="amendements", lazy="joined")

    # Extras. (TODO: move to dedicated table?)
    avis = Column(Text, nullable=True)  # type: Optional[str]
    observations = Column(Text, nullable=True)  # type: Optional[str]
    reponse = Column(Text, nullable=True)  # type: Optional[str]
    comments = Column(Text, nullable=True)  # type: Optional[str]
    bookmarked_at = Column(DateTime, nullable=True)

    __repr_keys__ = ("pk", "num", "rectif", "lecture_pk", "article_pk", "parent_pk")

    @classmethod
    def create(  # type: ignore
        cls,
        lecture,
        article,
        parent: "Amendement",
        num: int,
        rectif: int = 0,
        auteur: str = "",
        matricule: str = "",
        date_depot: str = None,
        sort: str = "",
        position: int = 0,
        discussion_commune: int = 0,
        identique: bool = False,
        dispositif: str = "",
        objet: str = "",
        resume: str = "",
        alinea: str = "",
        avis: str = "",
        observations: str = "",
        reponse: str = "",
        comments: str = "",
    ) -> "Amendement":
        amendement = cls(
            lecture=lecture,
            article=article,
            parent=parent,
            num=num,
            rectif=rectif,
            auteur=auteur,
            matricule=matricule,
            date_depot=date_depot,
            sort=sort,
            position=position,
            discussion_commune=discussion_commune,
            identique=identique,
            dispositif=dispositif,
            objet=objet,
            resume=resume,
            alinea=alinea,
            avis=avis,
            observations=observations,
            reponse=reponse,
            comments=comments,
        )
        DBSession.add(amendement)
        return amendement

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Amendement):
            return NotImplemented
        return self.sort_key < other.sort_key

    @property
    def sort_key(self) -> Tuple[int, int]:
        return (self.position or VERY_BIG_NUMBER, self.num)

    @property
    def num_str(self) -> str:
        return str(self.num)

    @property
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
        return GROUPS_COLORS.get(self.groupe, "#ffffff")

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

    ABANDONED = ("retiré", "irrecevable", "tombé")

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

    @property
    def gouvernemental(self) -> bool:
        return self.auteur == "LE GOUVERNEMENT"

    @property
    def is_displayable(self) -> bool:
        return (
            bool(self.avis) or self.gouvernemental
        ) and self.sort not in self.ABANDONED

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
        return self.avis == "Sagesse"

    @property
    def lecture_url_key(self) -> str:
        return (
            f"{self.lecture.chambre}.{self.lecture.session}."
            f"{self.lecture.num_texte}.{self.lecture.organe}"
        )

    def grouping_key(self) -> Tuple[str, str, str]:
        if self.gouvernemental:
            return (self.num_str, "", "")
        return (self.avis or "", self.observations or "", self.reponse or "")

    def asdict(self, full: bool = False) -> dict:
        result = {
            "num": self.num,
            "rectif": self.rectif or "",
            "pk": f"{self.num:06}",
            "sort": self.sort or "",
            "matricule": self.matricule or "",
            "gouvernemental": self.gouvernemental,
            "auteur": self.auteur,
            "groupe": self.groupe or "",
            "dispositif": self.dispositif,
            "objet": self.objet,
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
