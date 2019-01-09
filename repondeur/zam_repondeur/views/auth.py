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
        email = self.request.params["email"].strip().lower()
        user, created = get_one_or_create(User, email=email)
        user.last_login_at = datetime.utcnow()
        if created:
            DBSession.flush()
        headers = remember(self.request, user.pk)
        return HTTPFound(location=self.next_url, headers=headers)

    @property
    def next_url(self) -> Any:
        url = self.request.params.get("source")
        if url is None or url == self.request.route_url("login"):
            url = "/"
        return url


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
