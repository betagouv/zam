from typing import Dict

from .fetch import fetch_senateurs
from .parse import parse_senateurs
from .models import Senateur


def fetch_and_parse_senateurs() -> Dict[str, Senateur]:
    lines = fetch_senateurs()
    by_matricule = parse_senateurs(lines)  # type: Dict[str, Senateur]
    return by_matricule
