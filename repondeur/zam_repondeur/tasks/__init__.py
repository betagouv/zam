from pyramid.config import Configurator

from .huey import init_huey


def includeme(config: Configurator) -> None:
    """
    Called automatically via config.include("zam_repondeur.tasks")
    """
    init_huey(config.registry.settings)
