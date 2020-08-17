import enum


class Chambre(enum.Enum):
    AN = "Assemblée nationale"
    SENAT = "Sénat"
    CCFP = "Conseil commun de la fonction publique"
    CSFPE = "Conseil supérieur de la fonction publique d’État"

    @classmethod
    def from_string(cls, chambre: str) -> "Chambre":
        d = {name.lower(): value for name, value in cls.__members__.items()}
        try:
            return d[chambre]
        except KeyError as e:
            raise ValueError(f"Invalid string value {chambre!r} for Chambre") from e

    def __str__(self) -> str:
        return self.name.lower()
