import secrets
import string
from typing import Any, List, Optional

from more_itertools import ichunked
from paste.deploy.converters import asbool
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.request import Request
from pyramid.security import Authenticated, Everyone
from sqlalchemy.exc import OperationalError

from zam_repondeur.models import DBSession, User


def includeme(config: Configurator) -> None:
    settings = config.registry.settings

    # We identify a user using a signed cookie
    authn_policy = AuthenticationPolicy(
        settings["zam.auth_secret"],
        hashalg="sha512",
        max_age=int(settings["zam.auth_cookie_duration"]),
        secure=asbool(settings["zam.auth_cookie_secure"]),
        http_only=asbool(settings["zam.auth_cookie_http_only"]),
    )
    config.set_authentication_policy(authn_policy)

    # Add a "request.user" property
    config.add_request_method(get_user, "user", reify=True)

    # We protect access to certain views based on permissions,
    # that are granted to users based on ACLs added to resources
    authz_policy = ACLAuthorizationPolicy()
    config.set_authorization_policy(authz_policy)

    # Make all views "secure by default"
    config.set_default_permission("view")

    # Add routes for login, logout and welcome
    config.add_route("login", "/identification")
    config.add_route("email_sent", "/courriel-envoye")
    config.add_route("auth", "/authentification")
    config.add_route("logout", "/deconnexion")
    config.add_route("logout_confirm", "/deconnecte")
    config.add_route("welcome", "/bienvenue")


def get_user(request: Request) -> Optional[User]:
    """
    Find the user in the database based on the ID in the auth cookie
    """
    user_id = request.unauthenticated_userid
    if user_id is not None:
        try:
            user: Optional[User] = DBSession.query(User).get(user_id)
        except OperationalError:
            return None
        if user and not request.is_xhr:
            user.record_activity()
        return user
    return None


class AuthenticationPolicy(AuthTktAuthenticationPolicy):
    def __init__(self, secret: str, **kwargs: Any) -> None:
        super().__init__(secret, **kwargs)

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
            if request.user.is_admin:
                principals.append("group:admins")
        return principals


def generate_auth_token(length: int = 20, chunk_size: int = 5) -> str:
    """
    We use the convenient APIs added in Python 3.6 for generating cryptographically
    strong random numbers suitable for authentication tokens.

    See https://docs.python.org/3/library/secrets.html
    """
    alphabet = string.ascii_uppercase + string.digits
    chars = (secrets.choice(alphabet) for _ in range(length))
    chunks = ("".join(chunk) for chunk in ichunked(chars, chunk_size))
    return "-".join(chunks)
