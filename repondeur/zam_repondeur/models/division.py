from typing import NamedTuple, Optional


class SubDiv(NamedTuple):
    type_: str
    num: str
    mult: str
    pos: str

    @classmethod
    def create(
        cls,
        type_: str,
        num: Optional[str] = None,
        mult: Optional[str] = None,
        pos: Optional[str] = None,
    ) -> "SubDiv":
        return cls(
            type_=type_,
            num="" if num is None else num,
            mult="" if mult is None else mult,
            pos="" if pos is None else pos,
        )


ADJECTIFS_MULTIPLICATIFS = {
    "bis": 2,
    "ter": 3,
    "quater": 4,
    "quinquies": 5,
    "sexies": 6,
    "septies": 7,
    "octies": 8,
    "nonies": 9,
    "novies": 9,
    "decies": 10,
    "undecies": 11,
    "duodecies": 12,
    "terdecies": 13,
    "quaterdecies": 14,
    "quindecies": 15,
    "sexdecies": 16,
    "septdecies": 17,
    "octodecies": 18,
    "novodecies": 19,
    "vicies": 20,
    "unvicies": 21,
    "duovicies": 22,
    "tervicies": 23,
    "quatervicies": 24,
    "quinvicies": 25,
    "sexvicies": 26,
    "septvicies": 27,
    "duodetrecies": 28,
    "undetricies": 29,
    "tricies": 30,
}
