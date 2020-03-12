from typing import Any

from pyramid.config import Configurator
from pyramid.router import Router

from zam_repondeur import BASE_SETTINGS


def make_app(global_settings: dict, **settings: Any) -> Router:

    settings = {**BASE_SETTINGS, **settings}

    with Configurator(settings=settings) as config:

        config.include("zam_repondeur")

        # Custom app name
        config.add_settings({"zam.app_name": "Visam"})

        # Custom logo
        config.override_asset(
            to_override="zam_repondeur:static/",
            override_with="zam_repondeur:visam/static/",
        )

        # Scan Visam-specific views
        config.scan(".views")

        app = config.make_wsgi_app()

    return app
