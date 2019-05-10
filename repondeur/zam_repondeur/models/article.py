import logging
from datetime import datetime
from itertools import groupby
from typing import Iterable, List, Optional, Tuple, TYPE_CHECKING

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    PickleType,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship, validates

from zam_repondeur.decorator import reify

from .base import Base, DBSession
from .amendement import Amendement, Reponse
from .division import ADJECTIFS_MULTIPLICATIFS, SubDiv

# Make this type available to mypy, but avoid circular imports
if TYPE_CHECKING:
    from .lecture import Lecture  # noqa


logger = logging.getLogger(__name__)


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

ALLOWED_POS = ("avant", "", "après")


class ArticleUserContent(Base):
    __tablename__ = "article_user_contents"

    pk: int = Column(Integer, primary_key=True)
    title: Optional[str] = Column(Text, nullable=True)
    presentation: Optional[str] = Column(Text, nullable=True)

    article_pk: int = Column(Integer, ForeignKey("articles.pk"), nullable=False)
    article: "Article" = relationship("Article", back_populates="user_content")


class Article(Base):
    __tablename__ = "articles"
    __table_args__ = (
        Index("ix_articles__lecture_pk", "lecture_pk"),
        UniqueConstraint("lecture_pk", "type", "num", "mult", "pos"),
    )

    pk: int = Column(Integer, primary_key=True)
    created_at: datetime = Column(DateTime, nullable=False)

    lecture_pk: int = Column(Integer, ForeignKey("lectures.pk"), nullable=False)
    lecture: "Lecture" = relationship("Lecture", back_populates="articles")
    type: str = Column(Text, nullable=False, default="")
    num: str = Column(Text, nullable=False, default="")
    mult: str = Column(Text, nullable=False, default="")
    pos: str = Column(Text, nullable=False, default="")
    content: Optional[dict] = Column(PickleType, nullable=True)

    amendements = relationship(
        Amendement,
        order_by=(Amendement.position, Amendement.num),
        back_populates="article",
    )

    user_content = relationship(
        ArticleUserContent,
        back_populates="article",
        uselist=False,
        lazy="joined",
        cascade="all, delete-orphan",
    )

    events = relationship(
        "Event",
        order_by="Event.created_at.desc()",
        cascade="all, delete-orphan",
        backref="article",
    )

    @validates("type")
    def validate_type(self, key: str, type: str) -> str:
        return validate(key, type, ALLOWED_TYPE)

    @validates("pos")
    def validate_pos(self, key: str, pos: str) -> str:
        return validate(key, pos, ALLOWED_POS)

    def matches(self, subdiv: SubDiv) -> bool:
        return (
            self.type == subdiv.type_
            and self.num == subdiv.num
            and self.mult == subdiv.mult
            and self.pos == subdiv.pos
        )

    __repr_keys__ = ("pk", "lecture_pk", "type", "num", "mult", "pos")

    def __str__(self) -> str:
        type_parts = [
            self.pos or "",
            "art." if self.type == "article" else self.type or "",
        ]
        return self._format_helper(type_parts)

    def format(self, short: bool = False) -> str:
        type_ = "art." if self.type == "article" and short else self.type or ""
        type_parts = [type_]
        if self.pos:
            type_parts += ["add.", f"{self.pos[:2]}."]
        return self._format_helper(type_parts)

    def _format_helper(self, type_parts: List[str]) -> str:
        if self.type == "annexe" and not self.num:
            return "Annexes"
        parts = type_parts + [self._num_disp, self.mult or ""]
        non_empty_parts = (part for part in parts if part)
        capitalized_parts = (
            part.capitalize() if index == 0 else part
            for index, part in enumerate(non_empty_parts)
        )
        return " ".join(capitalized_parts)

    @property
    def _num_disp(self) -> str:
        if self.type == "article" and self.num == "0":
            return "liminaire"
        return self.num or ""

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Article):
            return NotImplemented
        if self.lecture != other.lecture:
            raise ValueError
        return bool(
            (self.type == other.type)
            and (self.num == other.num)
            and (self.mult == other.mult)
            and (self.pos == other.pos)
        )

    _ORDER_TYPE = {
        "titre": 1,
        "motion": 2,
        "chapitre": 3,
        "section": 4,
        "sous-section": 5,
        "article": 6,
        "annexe": 7,
        "": 8,
    }

    _ORDER_MULT = {"": 1, **ADJECTIFS_MULTIPLICATIFS}

    _ORDER_POS = {"avant": 0, "": 1, "apres": 2, "après": 2}

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Article):
            return NotImplemented
        if self.lecture != other.lecture:
            raise ValueError
        return self.sort_key < other.sort_key

    @reify
    def sort_key(self) -> Tuple[int, str, Tuple[int, str], int]:
        return (
            Article._ORDER_TYPE[self.type or ""],
            str(self.num or "").zfill(3),
            _mult_key(self.mult or ""),
            Article._ORDER_POS[self.pos or ""],
        )

    @reify
    def sort_key_as_str(self) -> str:
        s = self.sort_key
        return "|".join(map(str, (s[0], f"{s[1]}", f"{s[2][0]:02}", s[2][1], s[3])))

    @classmethod
    def create(
        cls,
        lecture: "Lecture",
        type: str,
        num: str = "",
        mult: str = "",
        pos: str = "",
        content: dict = {},
    ) -> "Article":
        now = datetime.utcnow()
        article = cls(
            lecture=lecture,
            type=type,
            num=num,
            mult=mult,
            pos=pos,
            content=content,
            created_at=now,
        )
        user_content = ArticleUserContent(article=article, title="", presentation="")
        DBSession.add(user_content)
        return article

    @property
    def previous_article(self) -> Optional["Article"]:
        sorted_articles: List[Article] = sorted(self.lecture.articles)
        previous_index = sorted_articles.index(self) - 1
        if previous_index < 0:
            return None
        return sorted_articles[previous_index]

    @property
    def previous_displayable_article(self) -> Optional["Article"]:
        previous_article = self.previous_article
        if previous_article and previous_article.pos:
            while previous_article:
                for amendement in previous_article.amendements:
                    if amendement.is_displayable:
                        return previous_article
                previous_article = previous_article.previous_article
                if previous_article and not previous_article.pos:
                    return previous_article
        return previous_article

    @property
    def next_article(self) -> Optional["Article"]:
        sorted_articles: List[Article] = sorted(self.lecture.articles)
        next_index = sorted_articles.index(self) + 1
        if next_index >= len(sorted_articles):
            return None
        return sorted_articles[next_index]

    @property
    def next_displayable_article(self) -> Optional["Article"]:
        next_article = self.next_article
        if next_article and next_article.pos:
            while next_article:
                for amendement in next_article.amendements:
                    if amendement.is_displayable:
                        return next_article
                next_article = next_article.next_article
                if next_article and not next_article.pos:
                    return next_article
        return next_article

    @property
    def slug(self) -> str:
        parts = []
        if self.type:
            parts.append(self.type)
        if self.pos:
            parts.extend(["add", self.pos[:2]])
        parts.append(str(self.num))
        if self.mult:
            parts.append(self.mult.replace(" ", "-"))
        return "-".join([part.lower() for part in parts])

    @property
    def url_key(self) -> str:
        return f"{self.type}.{self.num}.{self.mult}.{self.pos}"

    def grouped_displayable_amendements(
        self
    ) -> Iterable[Tuple[Reponse, List[Amendement]]]:
        return self.group_amendements(
            amdt for amdt in self.amendements if amdt.is_displayable
        )

    def grouped_displayable_top_level_amendements(
        self
    ) -> Iterable[Tuple[Reponse, List[Amendement]]]:
        return self.group_amendements(
            amdt
            for amdt in self.amendements
            if amdt.is_displayable and not amdt.is_sous_amendement
        )

    def group_amendements(
        self, amendements: Iterable[Amendement]
    ) -> Iterable[Tuple[Reponse, List[Amendement]]]:
        return (
            (reponse, list(group))
            for reponse, group in groupby(amendements, key=Amendement.full_reponse)
        )

    def asdict(self) -> dict:
        return {
            "sort_key_as_str": self.sort_key_as_str,
            "title": self.user_content.title or "",
            "presentation": self.user_content.presentation or "",
        }


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


def _mult_key(s: str) -> Tuple[int, str]:
    if " " in s:
        mult, intersticiel = s.split(" ", 1)
    else:
        if s in Article._ORDER_MULT:
            mult, intersticiel = s, ""
        else:
            mult, intersticiel = "", s
    return (Article._ORDER_MULT.get(mult, 0), intersticiel.ljust(10, "_"))
