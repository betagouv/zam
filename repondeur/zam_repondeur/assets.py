from pyramid.config import Configurator
from pyramid.static import ManifestCacheBuster


def includeme(config: Configurator) -> None:
    config.add_static_view("static", "static", cache_max_age=3600)
    config.add_cache_buster(
        "zam_repondeur:static/",
        ManifestCacheBuster("zam_repondeur:static/manifest.json"),
    )
