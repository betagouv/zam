from typing import Dict

from .fetch import fetch_senateurs
from .models import Senateur
from .parse import parse_senateurs


def fetch_and_parse_senateurs() -> Dict[str, Senateur]:
    # 2019-10-11: encoding of the CSV file changed from CP1252 to UTF-8 without warning
    data = fetch_senateurs()
    for encoding in ["utf-8", "cp1252"]:
        try:
            lines = data.decode(encoding).splitlines()
            by_matricule: Dict[str, Senateur] = parse_senateurs(lines)
            return by_matricule
        except (UnicodeDecodeError, KeyError):
            continue
    raise ValueError("Failed to parse sénateurs CSV")
