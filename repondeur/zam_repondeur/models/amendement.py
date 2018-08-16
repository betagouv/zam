import re
from typing import Tuple

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, Text
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


class Amendement(Base):  # type: ignore
    __tablename__ = "amendements"

    pk = Column(Integer, primary_key=True)

    # Meta informations.
    num = Column(Integer)
    rectif = Column(Integer, nullable=False, default=0)
    auteur = Column(Text, nullable=True)
    matricule = Column(Text, nullable=True)
    groupe = Column(Text, nullable=True)
    date_depot = Column(Date, nullable=True)
    sort = Column(Text, nullable=True)

    # Ordre et regroupement lors de la discussion.
    position = Column(Integer, nullable=True)
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
    parent = relationship("Amendement", uselist=False, primaryjoin=(parent_pk == pk))
    lecture_pk = Column(Integer, ForeignKey("lectures.pk"))
    lecture = relationship("Lecture", back_populates="amendements")
    article_pk = Column(Integer, ForeignKey("articles.pk"))
    article = relationship("Article", back_populates="amendements", lazy="joined")

    # Extras. (TODO: move to dedicated table?)
    avis = Column(Text, nullable=True)
    observations = Column(Text, nullable=True)
    reponse = Column(Text, nullable=True)
    comments = Column(Text, nullable=True)
    bookmarked_at = Column(DateTime, nullable=True)

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
        date_depot: str = "",
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

    @property
    def num_disp(self) -> str:
        text = str(self.num)
        if self.rectif > 0:
            text += " rect."
        if self.rectif > 1:
            if self.rectif not in self._RECTIF_TO_SUFFIX:
                raise NotImplementedError
            text += " "
            text += self._RECTIF_TO_SUFFIX[self.rectif]
        return text

    @property
    def num_str(self) -> str:
        return str(self.num)

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

    _NUM_RE = re.compile(r"(?P<num>\d+)(?P<rect> rect\.(?: (?P<suffix>\w+))?)?")

    ABANDONED = ("retiré", "irrecevable", "tombé")

    @staticmethod
    def parse_num(text: str) -> Tuple[int, int]:
        if text == "":
            return 0, 0
        if text.startswith("COM-"):
            start = len("COM-")
            text = text[start:]

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
        return bool(self.auteur == "LE GOUVERNEMENT")

    @property
    def is_displayable(self) -> bool:
        return (
            bool(self.avis) or self.gouvernemental
        ) and self.sort not in self.ABANDONED

    @property
    def lecture_url_key(self) -> str:
        return (
            f"{self.lecture.chambre}.{self.lecture.session}."
            f"{self.lecture.num_texte}.{self.lecture.organe}"
        )

    @property
    def article_url_key(self) -> str:
        return (
            f"{self.article.type}.{self.article.num}."
            f"{self.article.mult}.{self.article.pos}"
        )

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
            result["subdiv_type"] = self.article.type
            result["subdiv_titre"] = self.article.titre
            result["subdiv_num"] = self.article.num
            result["subdiv_pos"] = self.article.pos
            result["subdiv_mult"] = self.article.mult
        return result
