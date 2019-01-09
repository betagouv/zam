from datetime import datetime
from typing import Any

from pyramid.httpexceptions import HTTPFound
from pyramid.request import Request
from pyramid.security import NO_PERMISSION_REQUIRED, remember, forget
from pyramid.view import forbidden_view_config, view_config, view_defaults

from zam_repondeur.models import DBSession, User, get_one_or_create


@view_defaults(route_name="login", permission=NO_PERMISSION_REQUIRED)
class Login:
    def __init__(self, request: Request) -> None:
        self.request = request

    @view_config(request_method="GET", renderer="login.html")
    def get(self) -> Any:
        # Skip the form if we're already logged in
        if self.request.unauthenticated_userid:
            return HTTPFound(location=self.next_url)
        return {}

    @view_config(request_method="POST")
    def post(self) -> Any:
        email = User.normalize_email(self.request.params["email"])

        user, created = get_one_or_create(User, email=email)
        if created:
            DBSession.flush()  # so that the DB assigns a value to user.pk

        user.last_login_at = datetime.utcnow()

        next_url = self.next_url
        if not user.name:
            next_url = self.request.route_url("welcome", _query={"source": next_url})
        elif not user.teams:
            next_url = self.request.route_url("join_team", _query={"source": next_url})

        headers = remember(self.request, user.pk)

        return HTTPFound(location=next_url, headers=headers)

    @property
    def next_url(self) -> Any:
        url = self.request.params.get("source")
        if url is None or url == self.request.route_url("login"):
            url = "/"
        return url


@view_defaults(route_name="welcome")
class Welcome:
    def __init__(self, request: Request) -> None:
        self.request = request

    @view_config(request_method="GET", renderer="welcome.html")
    def get(self) -> Any:
        return {"name": self.request.user.name or self.request.user.default_name()}

    @view_config(request_method="POST")
    def post(self) -> Any:
        self.request.user.name = User.normalize_name(self.request.params["name"])
        next_url = self.request.params.get("source") or "/"
        if not self.request.user.teams:
            next_url = self.request.route_url("join_team", _query={"source": next_url})
        return HTTPFound(location=next_url)


@view_config(route_name="logout", permission=NO_PERMISSION_REQUIRED)
def logout(request: Request) -> Any:
    """
    Clear the authentication cookie
    """
    headers = forget(request)
    next_url = request.route_url("login")
    return HTTPFound(location=next_url, headers=headers)


@forbidden_view_config()
def forbidden_view(request: Request) -> Any:
    """
    Redirect to login page when the user is not allowed to access the page
    """
    next_url = request.route_url("login", _query={"source": request.url})
    return HTTPFound(location=next_url)
