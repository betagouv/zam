import re
from datetime import date
from typing import Optional

from attr import (
    asdict,
    attrs,
    attrib,
    evolve,
)


@attrs
class Amendement:

    article: str = attrib()                 # libellé de l'article
    alinea: str = attrib()                  # libellé de l'alinéa
    num: str = attrib()                     # numéro d'amendement
    auteur: str = attrib()

    date_depot: Optional[date] = attrib(default=None)

    discussion_commune: Optional[bool] = attrib(default=None)
    identique: Optional[bool] = attrib(default=None)

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
        return evolve(self, **changes)

    def as_dict(self):
        return asdict(self)
