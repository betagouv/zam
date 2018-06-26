import base64
from typing import Any, List, Optional

from dataclasses import dataclass, field


@dataclass
class Article:
    pk: str
    id: int
    titre: str
    etat: Optional[str] = ""
    multiplicatif: Optional[str] = ""
    jaune: Optional[str] = ""
    alineas: Optional[dict] = None
    amendements: Any = field(default_factory=lambda: [])  # List[Amendement]
    document: Optional[str] = ""

    def __str__(self) -> str:
        if self.etat:
            return f"{self.id} {self.etat} {self.multiplicatif}".strip()
        return f"{self.id} {self.multiplicatif}".strip()

    @property
    def slug(self) -> str:
        return f'article-{str(self).replace(" ", "-")}'


@dataclass
class Amendement:
    pk: str
    id: int
    groupe: dict
    article: Article
    gouvernemental: bool = False
    auteur: Optional[str] = ""
    objet: Optional[str] = ""
    dispositif: Optional[str] = ""
    resume: Optional[str] = ""
    document: Optional[str] = ""
    etat: Optional[str] = ""

    def __str__(self) -> str:
        return self.pk


@dataclass
class Reponse:
    pk: str
    avis: str
    presentation: str
    content: str
    amendements: List[Amendement]
    article: Article

    def __str__(self) -> str:
        return self.pk

    @staticmethod
    def pk_from_raw(raw: dict) -> str:
        unique = raw.get("presentation", str(raw["idReponse"]))
        return base64.b64encode(unique.encode()).decode()

    @property
    def favorable(self):
        return self.avis.startswith("Favorable")

    @property
    def sagesse(self):
        return self.avis == "Sagesse"
