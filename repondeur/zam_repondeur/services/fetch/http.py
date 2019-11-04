from typing import Optional

import requests
from cachecontrol import CacheControl
from cachecontrol.caches.file_cache import FileCache
from pyramid.config import Configurator
from pyramid.registry import Registry
from pyramid.threadlocal import get_current_registry
from zope.interface import Interface


class IHTTPSession(Interface):
    pass


def includeme(config: Configurator) -> None:
    """
    Called automatically via config.include("zam_repondeur.services.fetch.http")
    """
    session = requests.session()
    http_cache_dir = config.registry.settings["zam.http_cache_dir"]
    cached_session = CacheControl(session, cache=FileCache(http_cache_dir))
    config.registry.registerUtility(component=cached_session, provided=IHTTPSession)


def get_http_session(registry: Optional[Registry] = None) -> CacheControl:
    if registry is None:
        registry = get_current_registry()
    return registry.queryUtility(IHTTPSession)
