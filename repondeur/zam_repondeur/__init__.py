from multiprocessing import cpu_count
from typing import Any, List, Optional

from paste.deploy.converters import asbool
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.request import Request
from pyramid.router import Router
from pyramid.security import Authenticated, Everyone
from pyramid.session import JSONSerializer, SignedCookieSessionFactory
from pyramid.view import view_config
from sqlalchemy import engine_from_config, event

from zam_repondeur.errors import extract_settings, setup_rollbar_log_handler
from zam_repondeur.models import DBSession, Base, Team, User, log_query_with_origin
from zam_repondeur.resources import Root
from zam_repondeur.tasks.huey import init_huey
from zam_repondeur.version import load_version


FILTERS_PATH = "zam_repondeur.views.jinja2_filters"
BASE_SETTINGS = {
    "jinja2.filters": {
        "paragriphy": f"{FILTERS_PATH}:paragriphy",
        "amendement_matches": f"{FILTERS_PATH}:amendement_matches",
        "filter_out_empty_additionals": f"{FILTERS_PATH}:filter_out_empty_additionals",
        "group_by_day": f"{FILTERS_PATH}:group_by_day",
    },
    "jinja2.undefined": "strict",
    "zam.auth_cookie_duration": 7 * 24 * 3600,  # a user stays identified for 7 days
    "zam.auth_cookie_secure": True,  # disable for local HTTP access in development
    "zam.legislatures": "14,15",
    "huey.workers": (cpu_count() * 2) + 1,
}


def make_app(global_settings: dict, **settings: Any) -> Router:

    settings = {**BASE_SETTINGS, **settings}

    session_factory = SignedCookieSessionFactory(
        secret=settings["zam.session_secret"], serializer=JSONSerializer()
    )

    with Configurator(
        settings=settings, root_factory=Root, session_factory=session_factory
    ) as config:

        rollbar_settings = extract_settings(settings, prefix="rollbar.")
        if "access_token" in rollbar_settings and "environment" in rollbar_settings:
            setup_rollbar_log_handler(rollbar_settings)

        setup_database(config, settings)

        setup_auth(config, settings)

        config.include("pyramid_default_cors")

        config.include("pyramid_jinja2")
        config.add_jinja2_renderer(".html")
        config.add_jinja2_search_path("zam_repondeur:templates", name=".html")

        config.add_route("choices_lectures", "/choices/dossiers/{uid}/")
        config.add_route("error", "/error")

        config.include("zam_repondeur.assets")

        init_huey(settings)
        config.include("zam_repondeur.data")
        load_version(config)

        config.scan()

        app = config.make_wsgi_app()

    return app


@view_config(route_name="error")
def error(request: Request) -> None:
    raise Exception("Not a real error (just for testing)")


def setup_database(config: Configurator, settings: dict) -> None:

    config.include("pyramid_tm")

    engine = engine_from_config(
        settings, "sqlalchemy.", connect_args={"application_name": "zam_webapp"}
    )
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    if asbool(settings.get("zam.log_sql_queries_with_origin")):
        event.listen(engine, "before_cursor_execute", log_query_with_origin)


def setup_auth(config: Configurator, settings: dict) -> None:

    # We identify a user using a signed cookie
    authn_policy = AuthenticationPolicy(
        settings["zam.auth_secret"],
        hashalg="sha512",
        max_age=int(settings["zam.auth_cookie_duration"]),
        secure=asbool(settings["zam.auth_cookie_secure"]),
    )
    config.set_authentication_policy(authn_policy)

    # Add a "request.user" property
    config.add_request_method(get_user, "user", reify=True)

    # Add a "request.team" property
    config.add_request_method(get_team, "team", reify=True)

    # We protect access to certain views based on permissions,
    # that are granted to users based on ACLs added to resources
    authz_policy = ACLAuthorizationPolicy()
    config.set_authorization_policy(authz_policy)

    # Make all views "secure by default"
    config.set_default_permission("view")

    # Add routes for login, logout and welcome
    config.add_route("login", "/identification")
    config.add_route("logout", "/deconnexion")
    config.add_route("welcome", "/bienvenue")


def get_user(request: Request) -> Optional[User]:
    """
    Find the user in the database based on the ID in the auth cookie
    """
    user_id = request.unauthenticated_userid
    if user_id is not None:
        user: Optional[User] = DBSession.query(User).get(user_id)
        return user
    return None


def get_team(request: Request) -> Optional[Team]:
    team_name = request.environ.get("HTTP_X_REMOTE_USER")
    if team_name is None:
        return None
    team: Optional[Team] = DBSession.query(Team).filter_by(name=team_name).first()
    if team is None:
        team = Team.create(name=team_name)
        DBSession.flush()
    return team


class AuthenticationPolicy(AuthTktAuthenticationPolicy):
    def authenticated_userid(self, request: Request) -> Optional[int]:
        """
        Return the authenticated userid or None if no authenticated userid
        can be found. This method of the policy should ensure that a record
        exists in whatever persistent store is used related to the user
        (the user should not have been deleted); if a record associated
        with the current id does not exist in a persistent store, it should
        return None.
        """
        user: Optional[User] = request.user
        if user is not None:
            user_id: int = user.pk
            return user_id
        return None

    def effective_principals(self, request: Request) -> List[str]:
        """
        Return a sequence representing the effective principals typically
        including the userid and any groups belonged to by the current user,
        always including 'system' groups such as pyramid.security.Everyone
        and pyramid.security.Authenticated.
        """
        principals = [Everyone]
        if request.user is not None:
            principals.append(Authenticated)
            principals.append(f"user:{request.user.pk}")
            for team in request.user.teams:
                principals.append(f"team:{team.pk}")
        return principals
