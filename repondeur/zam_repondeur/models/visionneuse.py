import base64
from collections import OrderedDict
from hashlib import sha256
from typing import DefaultDict, List, Optional

from dataclasses import dataclass, field

from zam_repondeur.constants import GROUPS_COLORS

from .amendement import Amendement as AmendementModel


@dataclass
class Reponse:
    pk: str
    avis: str
    presentation: str
    content: str

    def __str__(self) -> str:
        return self.pk

    def __hash__(self) -> int:
        return hash(self.pk)

    @staticmethod
    def pk_from_raw(raw: dict) -> str:
        unique = raw.get("presentation", str(raw["idReponse"]))
        return base64.b64encode(unique.encode()).decode()

    @property
    def favorable(self) -> bool:
        return self.avis.startswith("Favorable")

    @property
    def sagesse(self) -> bool:
        return self.avis == "Sagesse"


@dataclass
class Amendement:
    pk: str
    id: int
    groupe: dict
    reponse: Reponse
    num_disp: str
    gouvernemental: bool = False
    auteur: Optional[str] = ""
    parent: Optional[str] = ""
    objet: Optional[str] = ""
    dispositif: Optional[str] = ""
    resume: Optional[str] = ""
    document: Optional[str] = ""
    sort: Optional[str] = ""

    def __str__(self) -> str:
        return self.num_disp

    @classmethod
    def create(cls, amendement: AmendementModel, reponse: Reponse) -> "Amendement":
        parent = amendement.parent
        return cls(  # type: ignore
            pk=f"{amendement.num:06}",
            id=amendement.num,
            groupe={
                "libelle": amendement.groupe,
                "couleur": GROUPS_COLORS.get(amendement.groupe, "#ffffff"),
            },
            reponse=reponse,
            num_disp=amendement.num_disp,
            auteur=amendement.auteur,
            dispositif=amendement.dispositif,
            objet=amendement.objet,
            resume=amendement.resume,
            sort=amendement.sort,
            gouvernemental=amendement.gouvernemental,
            parent=parent and parent.num_disp or "",
        )


@dataclass
class Article:
    pk: str
    id: int
    titre: str
    etat: Optional[str] = ""
    multiplicatif: Optional[str] = ""
    type_: str = ""
    jaune: Optional[str] = ""
    alineas: Optional[dict] = None
    reponses: DefaultDict[Reponse, List[Amendement]] = field(
        default_factory=lambda: DefaultDict(list)
    )
    document: Optional[str] = ""

    def __str__(self) -> str:
        if self.etat:
            return f"add. {self.etat}. {self.id} {self.multiplicatif}".strip()
        return f"{self.id} {self.multiplicatif}".strip()

    @property
    def slug(self) -> str:
        return f'article-{str(self).replace(" ", "-").replace(".", "")}'


class Articles(OrderedDict):
    def get_or_create(self, amendement: AmendementModel) -> Article:
        pk = f"{amendement.article.num}-{amendement.article.mult}"
        if amendement.article.pos:
            pk += f"-{amendement.article.pos}"
        if pk in self:
            article: Article = self[pk]
        else:
            article: Article = Article(  # type: ignore
                pk=pk,
                id=amendement.article.num,
                titre=amendement.article.titre,
                multiplicatif=amendement.article.mult,
                etat=amendement.article.pos[:2],
                type_=amendement.article.type,
                jaune=amendement.article.jaune,
                alineas=amendement.article.contenu,
            )
            self[pk] = article
        return article


def build_tree(amendements: List[AmendementModel]) -> OrderedDict:
    articles = Articles()
    for index, amendement in enumerate(amendements, 1):
        if amendement.is_displayable:
            article = articles.get_or_create(amendement)
            if amendement.gouvernemental:
                # Avoid later regroup by same (inexisting) response.
                reponse_pk = str(index)
            else:
                reponse_pk = base64.b64encode(
                    sha256(getattr(amendement, "reponse", "").encode()).digest()
                ).decode()
            reponse = Reponse(  # type: ignore
                pk=reponse_pk,
                avis=amendement.avis,
                presentation=amendement.observations or "",
                content=amendement.reponse or "",
            )
            amd = Amendement.create(amendement, reponse)
            article.reponses[reponse].append(amd)
    return articles
