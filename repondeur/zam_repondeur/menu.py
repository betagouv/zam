from typing import Any, List, Optional

from pyramid.config import Configurator
from pyramid.request import Request
from zope.interface import Attribute, Interface, implementer


class IMenuAction(Interface):
    """
    Entry in the main menu
    """

    def __init__(self, request: Request) -> None:
        pass

    title: str = Attribute("title")
    should_show: bool = Attribute("should_show")
    url: str = Attribute("url")
    tab_name: Optional[str] = Attribute("tab_name")


@implementer(IMenuAction)
class MenuAction:
    def __init__(self, request: Request):
        self.request = request


def includeme(config: Configurator) -> None:
    """
    Called automatically via config.include("zam_repondeur.menu")
    """
    config.add_directive("add_menu_action", add_menu_action)
    config.add_request_method(get_menu_actions, "get_menu_actions")


def add_menu_action(config: Configurator, menu_action: Any) -> None:
    def _add_menu_action() -> None:
        config.registry.registerUtility(menu_action, IMenuAction)

    config.action(None, _add_menu_action)


def get_menu_actions(request: Request) -> List[Any]:
    return [
        action(request) for _, action in request.registry.getUtilitiesFor(IMenuAction)
    ]
