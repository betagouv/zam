from datetime import datetime
from typing import Any, Dict

from pyramid.httpexceptions import HTTPFound
from pyramid.request import Request
from pyramid.security import NO_PERMISSION_REQUIRED, remember, forget
from pyramid.view import forbidden_view_config, view_config, view_defaults
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message as MailMessage

from zam_repondeur.auth import generate_auth_token
from zam_repondeur.message import Message
from zam_repondeur.models import DBSession, User, get_one_or_create
from zam_repondeur.resources import Root
from zam_repondeur.users import repository


@view_defaults(route_name="login", permission=NO_PERMISSION_REQUIRED, context=Root)
class UserLogin:
    def __init__(self, context: Root, request: Request) -> None:
        self.request = request
        self.context = context

    @view_config(request_method="GET", renderer="auth/user_login.html")
    def get(self) -> Any:
        # Skip the form if we're already logged in
        if self.request.unauthenticated_userid:
            return HTTPFound(location=self.next_url)
        return {}

    @property
    def next_url(self) -> Any:
        url = self.request.params.get("source")
        if url is None or url == self.request.route_url("login"):
            url = self.request.resource_url(self.context["lectures"])
        return url

    @view_config(request_method="POST")
    def post(self) -> Any:
        email = self.request.params.get("email")
        if not email:
            self.request.session["missing_email"] = True
            return HTTPFound(location=self.request.route_url("login"))

        email = User.normalize_email(email)
        if not User.validate_email(email):
            self.request.session["incorrect_email"] = True
            return HTTPFound(location=self.request.route_url("login"))

        if not User.validate_email_domain(email):
            self.request.session["incorrect_domain"] = True
            return HTTPFound(location=self.request.route_url("login"))

        token = generate_auth_token()
        repository.set_auth_token(email=email, token=token)

        url = self.request.route_url("auth", _query={"token": token})

        mailer = get_mailer(self.request)
        message = MailMessage(
            subject="Se connecter à Zam",
            sender="contact@zam.beta.gouv.fr",
            recipients=[email],
            body=f"""
Bonjour,

Pour vous connecter à Zam, veuillez cliquer sur l’adresse suivante :
{url}

Bonne journée !
            """.strip(),
        )
        mailer.send(message)

        return HTTPFound(
            location=self.request.route_url("email_sent", _query={"email": email})
        )


@view_config(
    route_name="email_sent",
    permission=NO_PERMISSION_REQUIRED,
    context=Root,
    renderer="auth/email_sent.html",
)
def email_sent(context: Root, request: Request) -> Dict[str, str]:
    email = request.params.get("email")
    if email is None:
        raise HTTPFound(location=request.route_url("login"))
    return {"email": email}


@view_defaults(route_name="auth", permission=NO_PERMISSION_REQUIRED, context=Root)
class Authenticate:
    def __init__(self, context: Root, request: Request) -> None:
        self.request = request
        self.context = context

    @view_config(request_method="GET")
    def get(self) -> Any:

        token = self.request.params.get("token")
        auth = repository.get_auth_token_data(token)
        if auth is None:
            self.request.session.flash(
                Message(
                    cls="error",
                    text="Le lien est invalide ou a expiré. Merci de renouveler votre demande.",  # noqa
                )
            )
            raise HTTPFound(location=self.request.route_url("login"))

        # Delete token from repository after it's been used successfully
        repository.delete_auth_token(token)

        email = auth.get("email")
        user, created = get_one_or_create(User, email=email)

        # Automatically add user without a team to the authenticated team
        if not user.teams and self.request.team is not None:
            user.teams.append(self.request.team)

        if created:
            DBSession.flush()  # so that the DB assigns a value to user.pk

        # Prevent from impersonating an existing member of another team
        if self.request.team and self.request.team not in user.teams:
            self.request.session["already_in_use"] = True
            return HTTPFound(location=self.request.route_url("login"))

        user.last_login_at = datetime.utcnow()

        next_url = self.next_url
        if not user.name:
            next_url = self.request.route_url("welcome", _query={"source": next_url})

        headers = remember(self.request, user.pk)

        self.request.session.flash(Message(cls="success", text="Bienvenue dans Zam !"))

        return HTTPFound(location=next_url, headers=headers)

    @property
    def next_url(self) -> Any:
        url = self.request.params.get("source")
        if url is None or url == self.request.route_url("login"):
            url = self.request.resource_url(self.context["lectures"])
        return url


@view_defaults(route_name="welcome", context=Root)
class Welcome:
    def __init__(self, context: Root, request: Request) -> None:
        self.request = request
        self.context = context

    @view_config(request_method="GET", renderer="auth/welcome.html")
    def get(self) -> Any:
        return {"name": self.request.user.name or self.request.user.default_name()}

    @view_config(request_method="POST")
    def post(self) -> Any:
        name = self.request.params.get("name")
        if not name:
            self.request.session["missing_name"] = True
            return HTTPFound(location=self.request.route_url("welcome"))

        self.request.user.name = User.normalize_name(name)
        next_url = self.request.params.get("source") or self.request.resource_url(
            self.context["lectures"]
        )
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

    # Redirect unauthenticated users to the login page
    if request.user is None:
        return HTTPFound(
            location=request.route_url("login", _query={"source": request.url})
        )

    # Redirect authenticated ones to the home page with an error message
    request.session.flash(
        Message(
            cls="warning",
            text="L’accès à cette lecture est réservé aux personnes autorisées.",
        )
    )
    return HTTPFound(location=request.resource_url(request.root))
