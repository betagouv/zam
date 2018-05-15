from typing import Any, List, NamedTuple, no_type_check


class Amendement(NamedTuple):
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


class Article(NamedTuple):
    pk: str
    id: str
    title: str
    content: str
    state: str
    multiplier: str
    jaune: str
    amendements: List[Amendement]

    def __str__(self) -> str:
        return f'{self.id} {self.state} {self.multiplier}'

    def __repr__(self) -> str:
        amendements = ','.join(str(amendement)
                               for amendement in self.amendements)
        return f'<Article {self} amendements={amendements}>'

    @no_type_check
    def __add__(self, amendement: Amendement):  # -> Article
        self.amendements.append(amendement)
        return self._replace(amendements=self.amendements)


class Reponse(NamedTuple):
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

    @no_type_check
    def __add__(self, amendement: Amendement):  # -> Reponse
        self.amendements.append(amendement)
        return self._replace(amendements=self.amendements)
