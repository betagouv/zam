import time
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from webob.multidict import MultiDict

from zam_repondeur.models import AVIS


def normalize_num(num: str) -> int:
    try:
        num_int = int(num)
    except ValueError:
        num_int = int(num.split("\n")[0].strip(","))
    return num_int


def normalize_avis(avis: str) -> str:
    avis = avis.strip()
    avis_lower = avis.lower()
    if avis_lower in ("défavorable", "defavorable"):
        avis = "Défavorable"
    elif avis_lower in ("favorable",):
        avis = "Favorable"
    elif avis_lower in ("sagesse",):
        avis = "Sagesse"
    elif avis_lower in ("retrait",):
        avis = "Retrait"
    if avis and avis not in AVIS:
        pass  # print(avis)
    return avis


def normalize_reponse(reponse: str, previous_reponse: str) -> str:
    reponse = reponse.strip()
    if reponse.lower() == "id.":
        reponse = previous_reponse
    return reponse


def add_url_fragment(url: str, fragment: str) -> str:
    scheme, netloc, path, params, query, _ = urlparse(url)
    return urlunparse((scheme, netloc, path, params, query, fragment))


def add_url_params(url: str, **extra_params: str) -> str:
    scheme, netloc, path, params, query, fragment = urlparse(url)
    query_dict = MultiDict(parse_qsl(query))
    query_dict.update(**extra_params)
    query = urlencode(query_dict)
    return urlunparse((scheme, netloc, path, params, query, fragment))


class Timer:
    start_time: float = 0.0
    stop_time: float = 0.0

    def start(self) -> None:
        self.start_time = time.monotonic()

    def stop(self) -> None:
        self.stop_time = time.monotonic()

    def __enter__(self) -> "Timer":
        self.start()
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, tb: Any) -> None:
        self.stop()

    def elapsed(self) -> float:
        return self.stop_time - self.start_time
