from typing import Any

from paste.deploy.converters import asbool
from pyramid.config import Configurator
from pyramid.request import Request
from pyramid.router import Router

from zam_repondeur import BASE_SETTINGS
from zam_repondeur.menu import MenuAction

from .auth import VisamAuthenticationPolicy
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

        authn_policy = VisamAuthenticationPolicy(
            settings["zam.auth_secret"],
            hashalg="sha512",
            max_age=int(settings["zam.auth_cookie_duration"]),
            secure=asbool(settings["zam.auth_cookie_secure"]),
            http_only=True,
        )
        config.set_authentication_policy(authn_policy)

        # Add Visam menu actions
        config.add_menu_action(MembersMenuAction)

        # Scan Visam-specific views
        config.scan(".views")

        app = config.make_wsgi_app()

    return app


class MembersMenuAction(MenuAction):
    tab_name = "members"

    title = "Gestion des membres"

    def __init__(self, request: Request):
        super().__init__(request)
        self.resource = self.request.root["members"]

    @property
    def should_show(self) -> bool:
        return self.request.has_permission("manage", self.resource)

    @property
    def url(self) -> str:
        return self.request.resource_url(self.resource)
