from huey import Huey
from pyramid.config import Configurator
from pyramid.request import Request
from zope.interface import Interface

from .huey import init_huey


class IHuey(Interface):
    pass


def includeme(config: Configurator) -> None:
    """
    Called automatically via config.include("zam_repondeur.tasks")
    """
    huey = init_huey(config.registry.settings)
    config.registry.registerUtility(component=huey, provided=IHuey)
    config.add_request_method(get_huey, "huey", reify=True)


def get_huey(request: Request) -> Huey:
    return request.registry.queryUtility(IHuey)
