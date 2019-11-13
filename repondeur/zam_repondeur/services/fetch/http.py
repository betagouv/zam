from typing import Any, Optional, Union

import requests
from cachecontrol import CacheControl, CacheController
from cachecontrol.caches.file_cache import FileCache
from cachecontrol.heuristics import ExpiresAfter
from pyramid.config import Configurator
from pyramid.registry import Registry
from pyramid.threadlocal import get_current_registry
from zope.interface import Interface


class CustomCacheController(CacheController):
    def __init__(
        self,
        cache: Any = None,
        cache_etags: bool = True,
        serializer: Any = None,
        status_codes: Optional[tuple] = None,
    ):
        # Explicitly add the 302 status code because the AN is returning
        # a lot of these and we want to avoid extra queries.
        status_codes = (200, 203, 300, 301) + (302,)
        super().__init__(cache, cache_etags, serializer, status_codes)


class IHTTPSession(Interface):
    pass


def includeme(config: Configurator) -> None:
    """
    Called automatically via config.include("zam_repondeur.services.fetch.http")
    """
    session = requests.session()
    http_cache_dir = config.registry.settings["zam.http_cache_dir"]
    http_cache_duration = int(config.registry.settings["zam.http_cache_duration"])
    cached_session = CacheControl(
        session,
        cache=FileCache(http_cache_dir),
        heuristic=ExpiresAfter(minutes=http_cache_duration),
        controller_class=CustomCacheController,
    )
    config.registry.registerUtility(component=cached_session, provided=IHTTPSession)


def get_http_session(
    registry: Optional[Registry] = None,
) -> Union[requests.Session, CacheControl]:
    if registry is None:
        registry = get_current_registry()
    cached_session = registry.queryUtility(IHTTPSession)
    if cached_session is None:
        return requests.session()  # fallback if cached session was not initialized
    return cached_session
