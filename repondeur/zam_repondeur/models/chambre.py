import enum


class Chambre(enum.Enum):
    AN = "Assemblée nationale"
    SENAT = "Sénat"
    CCFP = "Conseil commun de la fonction publique"

    @staticmethod
    def from_string(chambre: str) -> "Chambre":
        if chambre == "an":
            return Chambre.AN
        if chambre == "senat":
            return Chambre.SENAT
        if chambre == "ccfp":
            return Chambre.CCFP
        raise ValueError(f"Invalid string value {chambre!r} for Chambre")

    def __str__(self) -> str:
        return self.name.lower()
