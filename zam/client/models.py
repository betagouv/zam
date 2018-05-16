from typing import Any, List

from dataclasses import dataclass, field


@dataclass
class Amendement:
    pk: str
    id: str
    content: str
    article: Any  # :Article (cross-reference).
    authors: list
    group: dict
    summary: str

    def __str__(self) -> str:
        return self.pk

    def __repr__(self) -> str:
        return f'<Amendement {self} article={self.article}>'


@dataclass
class Article:
    pk: str
    id: str
    title: str
    state: str
    multiplier: str
    jaune: str
    content: str = 'TODO'
    amendements: List[Amendement] = field(default_factory=lambda: [])

    def __str__(self) -> str:
        return f'{self.id} {self.state} {self.multiplier}'

    def __repr__(self) -> str:
        amendements = ','.join(str(amendement)
                               for amendement in self.amendements)
        return f'<Article {self} amendements={amendements}>'


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

    def __repr__(self) -> str:
        amendements = ','.join(str(amendement)
                               for amendement in self.amendements)
        return (f'<Reponse {self} article={self.article}'
                f'amendements={amendements}>')
