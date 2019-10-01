from enum import Enum


class Phase(Enum):
    INCONNUE = 0
    PREMIERE_LECTURE = 1
    DEUXIEME_LECTURE = 2
    NOUVELLE_LECTURE = 3
    LECTURE_DEFINITIVE = 4

    def __lt__(self, other: "Phase") -> bool:
        return int(self.value) < int(other.value)

    @property
    def short_name(self) -> str:
        return _SHORT_NAMES[self]


_SHORT_NAMES = {
    Phase.INCONNUE: "?",
    Phase.PREMIERE_LECTURE: "1re lecture",
    Phase.DEUXIEME_LECTURE: "2e lecture",
    Phase.NOUVELLE_LECTURE: "Nouvelle lecture",
    Phase.LECTURE_DEFINITIVE: "Lecture définitive",
}
