from typing import Any

from pyramid.config import Configurator
from pyramid.router import Router

from zam_repondeur import BASE_SETTINGS

from .resources import VisamRoot


def make_app(global_settings: dict, **settings: Any) -> Router:

    settings = {**BASE_SETTINGS, **settings}

    with Configurator(settings=settings) as config:

        config.include("zam_repondeur")

        # Custom app name and contact email address
        config.add_settings(
            {
                "zam.app_name": "Visam",
                "zam.contact_email": "contact@visam.beta.gouv.fr",
            }
        )

        # Custom logo
        config.override_asset(
            to_override="zam_repondeur:static/",
            override_with="zam_repondeur:visam/static/",
        )

        # Custom templates
        config.add_jinja2_search_path("zam_repondeur:visam/templates", name=".html")

        # Customize the resource tree
        config.set_root_factory(VisamRoot)

        # Scan Visam-specific views
        config.scan(".views")

        app = config.make_wsgi_app()

    return app
