from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Iterator, Optional

from pyramid.config import Configurator
from pyramid.request import Request

# Make these types available to mypy, but avoid circular imports
if TYPE_CHECKING:
    from zam_repondeur.resources import Resource


def includeme(config: Configurator) -> None:
    """
    Called automatically via config.include("zam_repondeur.menu")
    """
    config.add_request_method(get_menu_actions, "get_menu_actions")


def get_menu_actions(request: Request) -> Iterator["MenuAction"]:
    for resource in request.context.self_and_parents:
        for menu_action_class in resource.menu_actions:
            yield menu_action_class(request, resource)


class MenuAction(ABC):
    """
    Base class for menu actions
    """

    def __init__(self, request: Request, resource: "Resource"):
        self.request = request
        self.resource = resource

    @property
    @abstractmethod
    def title(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def url(self) -> str:
        raise NotImplementedError

    @property
    def should_show(self) -> bool:
        return True

    # The menu entry will be highlighted as "selected" if the
    # "tab_name" variable in the template context matches this
    tab_name: Optional[str] = None

    # Optional CSS class for the link element
    link_class: Optional[str] = None

    # Make the browser open the link in a new window/tab
    open_in_new_window: bool = False
