from typing import Any, Optional

from paste.deploy.converters import asbool
from pyramid.config import Configurator
from pyramid.events import BeforeRender
from pyramid.router import Router

from zam_repondeur import BASE_SETTINGS

from .auth import VisamAuthenticationPolicy, VisamRequest
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

        # Custom authentication policy
        authn_policy = VisamAuthenticationPolicy(
            settings["zam.auth_secret"],
            hashalg="sha512",
            max_age=int(settings["zam.auth_cookie_duration"]),
            secure=asbool(settings["zam.auth_cookie_secure"]),
            http_only=True,
        )
        config.set_authentication_policy(authn_policy)

        # Custom request class with methods to identify different classes of users
        config.set_request_factory(VisamRequest)

        # Scan Visam-specific views
        config.scan(".views")

        config.add_subscriber(add_visam_renderer_globals, BeforeRender)

        app = config.make_wsgi_app()

    return app


def add_visam_renderer_globals(event: BeforeRender) -> None:
    """
    We want to use different accent colors for different classes of users
    """
    user_type = _get_user_type(event["request"])
    if user_type is not None:
        event["body_class"] = user_type


def _get_user_type(request: VisamRequest) -> Optional[str]:
    if request.is_admin_user:
        return "admin-user"
    if request.is_gouvernement_user:
        return "gouv-user"
    if request.is_member_user:
        return "member-user"
    return None
