"""
Everything Visam-specific
"""
from pyramid.config import Configurator


def includeme(config: Configurator) -> None:
    # Custom app name
    config.add_settings({"zam.app_name": "Visam"})

    # Custom logo
    config.override_asset(
        to_override="zam_repondeur:static/",
        override_with="zam_repondeur:visam/static/",
    )
