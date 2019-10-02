import os
from pathlib import Path

import requests
from cachecontrol import CacheControl
from cachecontrol.caches.file_cache import FileCache

HERE = Path(__file__)
DEFAULT_HTTP_CACHE_DIR = HERE.parent.parent.parent / ".web_cache"

HTTP_CACHE_DIR = os.environ.get("ZAM_HTTP_CACHE_DIR", DEFAULT_HTTP_CACHE_DIR)


session = requests.session()

cached_session = CacheControl(session, cache=FileCache(HTTP_CACHE_DIR))
