import enum


class Chambre(enum.Enum):
    AN = "Assemblée nationale"
    SENAT = "Sénat"

    @staticmethod
    def from_string(chambre: str) -> "Chambre":
        if chambre == "an":
            return Chambre.AN
        if chambre == "senat":
            return Chambre.SENAT
        raise ValueError(f"Invalid string value {chambre!r} for Chambre")

    def __str__(self) -> str:
        return self.name.lower()

    @property
    def short_name(self) -> str:
        return "AN" if self == Chambre.AN else "Sénat"
