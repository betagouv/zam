import logging
from datetime import datetime
from typing import Any, Dict
from urllib.parse import urlparse

from limiter import SlidingWindowLimiter
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPForbidden, HTTPFound, HTTPTooManyRequests
from pyramid.request import Request
from pyramid.response import Response
from pyramid.security import NO_PERMISSION_REQUIRED, ACLDenied, forget, remember
from pyramid.view import forbidden_view_config, view_config, view_defaults
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message as MailMessage

from zam_repondeur.auth import generate_auth_token
from zam_repondeur.message import Message
from zam_repondeur.models import DBSession, User, get_one_or_create
from zam_repondeur.resources import Root
from zam_repondeur.services.users import TokenAlreadyExists, repository

logger = logging.getLogger(__name__)


class RateLimiterMixin:
    request: Request

    def make_limiter(self, action: str, key: str) -> SlidingWindowLimiter:
        return SlidingWindowLimiter(
            threshold=self._get_max_actions_per_minute(action, key),
            interval=60,  # 1 minute
            redis_config=self.redis_config,
            name_space=f"{action}_per_{key}",
        )

    @reify
    def redis_config(self) -> Dict[str, Any]:
        settings = self.request.registry.settings
        url = urlparse(settings["zam.users.redis_url"])
        return {
            "host": url.hostname,
            "port": int(url.port or 6379),
            "db": int(url.path.replace("/", "")),
        }

    def _get_max_actions_per_minute(self, action: str, name: str) -> int:
        settings = self.request.registry.settings
        key = f"zam.users.max_{action}_per_{name}_per_minute"
        return int(settings[key])


@view_defaults(route_name="login", permission=NO_PERMISSION_REQUIRED, context=Root)
class UserLogin(RateLimiterMixin):
    def __init__(self, context: Root, request: Request) -> None:
        self.request = request
        self.email_limiter = self.make_limiter(action="token_requests", key="email")
        self.ip_limiter = self.make_limiter(action="token_requests", key="ip")

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
            url = self.request.resource_url(self.request.root["dossiers"])
        return url

    @view_config(request_method="POST", require_csrf=True)
    def post(self) -> Any:
        if self.ip_limiter.exceeded(self.request.remote_addr):
            return HTTPTooManyRequests()

        email = User.normalize_email(self.request.params.get("email"))

        if self.email_limiter.exceeded(email):
            return HTTPTooManyRequests()

        # Will usually be prevented by the browser (required)
        if not email:
            return self.invalid_email(email=email, reason="missing_email")

        # Will usually be prevented by the browser (type=email)
        if not User.email_is_well_formed(email):
            return self.invalid_email(email=email, reason="incorrect_email")

        # Will NOT be prevented by the browser (pattern=... is clumsy)
        if not User.email_is_allowed(email):
            return self.invalid_email(email=email, reason="incorrect_domain")

        token = self.create_auth_token(email)
        self.send_auth_token_email(token=token, email=email)
        self.log_successful_token_request(email)

        return HTTPFound(
            location=self.request.route_url("email_sent", _query={"email": email})
        )

    def invalid_email(self, email: str, reason: str) -> Response:
        self.log_failed_token_request(email)
        self.request.session[reason] = True
        return HTTPFound(location=self.request.route_url("login"))

    def create_auth_token(self, email: str) -> str:
        while True:
            token = generate_auth_token()
            try:
                repository.set_auth_token(email=email, token=token)
            except TokenAlreadyExists:
                logger.warning("Random token already exists, generating a new one")
            else:
                return token

    def send_auth_token_email(self, token: str, email: str) -> None:
        url = self.request.route_url("auth", _query={"token": token})
        url_dossiers = self.request.resource_url(self.request.root["dossiers"])
        mailer = get_mailer(self.request)
        message = MailMessage(
            subject="Se connecter à Zam",
            sender="contact@zam.beta.gouv.fr",
            recipients=[email],
            body=f"""
Bonjour,

Pour vous connecter à Zam, veuillez cliquer sur l’adresse suivante :
{url}

Ce lien contient un code personnel à usage unique,
valable 5 minutes, pour vous authentifier sur Zam.

Une fois connecté·e, vous pourrez directement accéder aux dossiers :
{url_dossiers}

Bonne journée !
            """.strip(),
        )
        mailer.send(message)

    def log_successful_token_request(self, email: str) -> None:
        ip = self.request.remote_addr
        logger.info("Successful token request by %r from %s", email, ip)

    def log_failed_token_request(self, email: str) -> None:
        ip = self.request.remote_addr
        logger.warning("Failed token request by %r from %s", email, ip)


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
class Authenticate(RateLimiterMixin):
    def __init__(self, context: Root, request: Request) -> None:
        self.request = request
        self.context = context
        self.ip_limiter = self.make_limiter(action="token_validations", key="ip")

    @view_config(request_method="GET")
    def get(self) -> Any:

        if self.ip_limiter.exceeded(self.request.remote_addr):
            return HTTPTooManyRequests()

        if self.request.unauthenticated_userid:
            return HTTPFound(location=self.next_url)

        token = self.request.params.get("token")
        auth = repository.get_auth_token_data(token)
        if auth is None:
            self.log_failed_login_attempt(token)
            self.request.session.flash(
                Message(
                    cls="error",
                    text="Le lien est invalide ou a expiré. Merci de renouveler votre demande.",  # noqa
                )
            )
            raise HTTPFound(location=self.request.route_url("login"))

        # Delete token from repository after it's been used successfully
        repository.delete_auth_token(token)

        email = auth["email"]
        user, created = get_one_or_create(User, email=email)

        if created:
            DBSession.flush()  # so that the DB assigns a value to user.pk

        self.log_successful_login_attempt(email)

        user.last_login_at = datetime.utcnow()

        next_url = self.next_url
        if not user.name:
            next_url = self.request.route_url("welcome", _query={"source": next_url})

        # Compute response headers for the session cookie
        headers = remember(self.request, user.pk)

        self.request.session.flash(Message(cls="success", text="Bienvenue dans Zam !"))

        return HTTPFound(location=next_url, headers=headers)

    @property
    def next_url(self) -> Any:
        url = self.request.params.get("source")
        if url is None or url == self.request.route_url("login"):
            url = self.request.resource_url(self.request.root["dossiers"])
        return url

    def log_successful_login_attempt(self, email: str) -> None:
        ip = self.request.remote_addr
        logger.info("Successful authentication by %r from %s", email, ip)

    def log_failed_login_attempt(self, token: str) -> None:
        ip = self.request.remote_addr
        logger.warning("Failed authentication attempt with token %r from %s", token, ip)


@view_defaults(route_name="welcome", context=Root)
class Welcome:
    def __init__(self, context: Root, request: Request) -> None:
        self.request = request

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
            self.request.root["dossiers"]
        )
        return HTTPFound(location=next_url)


@view_config(route_name="logout", permission=NO_PERMISSION_REQUIRED)
def logout(request: Request) -> Any:
    """
    Clear the authentication cookie
    """
    headers = forget(request)
    next_url = request.route_url("logout_confirm")
    return HTTPFound(location=next_url, headers=headers)


@view_config(
    route_name="logout_confirm",
    context=Root,
    renderer="auth/logout_confirm.html",
    permission=NO_PERMISSION_REQUIRED,
)
def logout_confirm(context: Root, request: Request) -> dict:
    """
    Make the user aware of the deconnexion.
    """
    return {}


@forbidden_view_config()
def forbidden_view(exception: HTTPForbidden, request: Request) -> Any:

    # Redirect unauthenticated users to the login page
    if request.user is None:
        return HTTPFound(
            location=request.route_url("login", _query={"source": request.url})
        )

    # Default
    message = "L’accès à ce dossier est réservé aux personnes autorisées."
    next_resource = request.root

    if isinstance(exception.result, ACLDenied):
        acl_denied: ACLDenied = exception.result
        if acl_denied.permission == "delete":
            message = "Vous n’êtes pas autorisé à supprimer ce dossier."
            next_resource = request.context
        elif acl_denied.permission == "retrait":
            message = "Vous n’êtes pas autorisé à retirer une personne de ce dossier."
            next_resource = request.context

    request.session.flash(Message(cls="warning", text=message))
    return HTTPFound(location=request.resource_url(next_resource))
