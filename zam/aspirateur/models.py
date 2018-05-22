import re
from dataclasses import (
    asdict,
    dataclass,
    replace,
)
from datetime import date
from typing import Optional


@dataclass
class Amendement:

    article: str        # libellé de l'article
    alinea: str         # libellé de l'alinéa
    num: str            # numéro d'amendement
    auteur: str

    date_depot: Optional[date] = None

    sort: Optional[str] = None  # retiré, adopté, etc.

    discussion_commune: Optional[bool] = None
    identique: Optional[bool] = None

    @property
    def num_int(self) -> int:
        """
        Numéro d'amendement sous forme purement numérique (sans suffixes)
        """
        mo = re.search(r'(\d+)', self.num)
        assert mo is not None
        return int(mo.group(1))

    def url(self, session, num_texte):
        return "http://www.senat.fr/amendements/{}/{}/{}".format(
            session,
            num_texte,
            self.html_page,
        )

    def evolve(self, **changes):
        return replace(self, **changes)

    def as_dict(self):
        return asdict(self)
