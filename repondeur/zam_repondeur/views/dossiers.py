from datetime import date
from typing import Iterator, List, Tuple

from paste.deploy.converters import aslist
from pyramid.httpexceptions import HTTPBadRequest, HTTPFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config, view_defaults
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message as MailMessage
from sqlalchemy.orm import joinedload

from zam_repondeur.message import Message
from zam_repondeur.models import DBSession, Dossier, Team, User, get_one_or_create
from zam_repondeur.models.events.dossier import (
    DossierActive,
    DossierDesactive,
    DossierRetrait,
    InvitationEnvoyee,
)
from zam_repondeur.resources import DossierCollection, DossierResource
from zam_repondeur.tasks.fetch import create_missing_lectures, update_dossier


class DossierCollectionBase:
    def __init__(self, context: DossierCollection, request: Request) -> None:
        self.context = context
        self.request = request
        self.dossiers = context.models(joinedload("team"))


@view_defaults(context=DossierCollection)
class DossierList(DossierCollectionBase):
    @view_config(request_method="GET", renderer="dossiers_list.html")
    def get(self) -> dict:
        my_dossiers = [
            dossier
            for dossier in self.dossiers
            if dossier.team
            and (self.request.user.is_admin or dossier.team in self.request.user.teams)
        ]
        return {
            "dossiers": my_dossiers,
            "allowed_to_activate": self.request.has_permission(
                "activate", self.context
            ),
        }


@view_defaults(context=DossierCollection, name="add", permission="activate")
class DossierAddForm(DossierCollectionBase):
    @view_config(request_method="GET", renderer="dossiers_add.html")
    def get(self) -> dict:
        available_dossiers = [dossier for dossier in self.dossiers if not dossier.team]
        return {"available_dossiers": available_dossiers}

    @view_config(request_method="POST")
    def post(self) -> Response:
        dossier_slug = self._get_dossier_slug()

        if not dossier_slug:
            self.request.session.flash(
                Message(cls="error", text="Ce dossier n’existe pas.")
            )
            return HTTPFound(location=self.request.resource_url(self.context))

        dossier = Dossier.get(slug=dossier_slug)

        if dossier is None:
            self.request.session.flash(
                Message(cls="error", text="Ce dossier n’existe pas.")
            )
            return HTTPFound(location=self.request.resource_url(self.context))

        if dossier.team:
            self.request.session.flash(
                Message(cls="warning", text="Ce dossier appartient à une autre équipe…")
            )
            return HTTPFound(location=self.request.resource_url(self.context))

        team = Team.create(name=dossier.slug)
        dossier.team = team
        admins_emails: List[str] = aslist(
            self.request.registry.settings.get("zam.auth_admins")
        )
        for admin in DBSession.query(User).filter(
            User.email.in_(admins_emails)  # type: ignore
        ):
            admin.teams.append(team)

        # Enqueue task to asynchronously add the lectures
        create_missing_lectures(dossier_pk=dossier.pk, user_pk=self.request.user.pk)

        DossierActive.create(dossier=dossier, request=self.request)

        self.request.session.flash(
            Message(
                cls="success",
                text=("Dossier créé avec succès, lectures en cours de création."),
            )
        )
        return HTTPFound(
            location=self.request.resource_url(self.context[dossier.url_key])
        )

    def _get_dossier_slug(self) -> str:
        try:
            dossier_slug = self.request.POST["dossier"] or ""
        except KeyError:
            raise HTTPBadRequest
        return dossier_slug


class DossierViewBase:
    def __init__(self, context: DossierResource, request: Request) -> None:
        self.context = context
        self.request = request
        self.dossier = context.dossier


@view_defaults(context=DossierResource)
class DossierView(DossierViewBase):
    @view_config(request_method="GET", renderer="dossier_item.html")
    def get(self) -> Response:
        return {
            "dossier": self.dossier,
            "dossier_resource": self.context,
            "current_tab": "dossier",
            "lectures": sorted(self.dossier.lectures),
            "allowed_to_delete": self.request.has_permission("delete", self.context),
        }

    @view_config(request_method="POST", permission="delete")
    def post(self) -> Response:
        DBSession.delete(self.dossier.team)
        for lecture in self.dossier.lectures:
            DBSession.delete(lecture)
        DBSession.flush()
        DossierDesactive.create(dossier=self.dossier, request=self.request)
        self.request.session.flash(
            Message(cls="success", text="Dossier supprimé avec succès.")
        )
        return HTTPFound(location=self.request.resource_url(self.context.parent))


@view_defaults(context=DossierResource, name="invite")
class DossierInviteForm(DossierViewBase):
    @view_config(request_method="GET", renderer="dossier_invite.html")
    def get(self) -> dict:
        return {
            "dossier": self.dossier,
            "dossier_resource": self.context,
            "team": self.dossier.team,
            "current_tab": "invite",
        }

    @view_config(request_method="POST")
    def post(self) -> Response:
        emails: str = self.request.POST.get("emails")

        new_users, existing_users = self._add_emails_to_team(emails, self.dossier.team)

        invitations_sent = 0
        if new_users:
            invitations_sent += self._send_new_users_invitations(new_users)
        if existing_users:
            invitations_sent += self._send_existing_users_invitations(existing_users)

        for user in new_users + existing_users:
            InvitationEnvoyee.create(
                dossier=self.dossier, email=user.email, request=self.request
            )

        if invitations_sent:
            if invitations_sent > 1:
                message = "Invitations envoyées avec succès."
            else:
                message = "Invitation envoyée avec succès."
            self.request.session.flash(Message(cls="success", text=message))
        else:
            self.request.session.flash(
                Message(
                    cls="warning",
                    text=(
                        "Aucune invitation n’a été envoyée, veuillez vérifier "
                        "les adresses de courriel qui doivent être en .gouv.fr"
                    ),
                )
            )
        return HTTPFound(location=self.request.resource_url(self.context))

    def _add_emails_to_team(
        self, emails: str, team: Team
    ) -> Tuple[List[User], List[User]]:
        new_users = []
        existing_users = []
        for email in self._cleaned_emails(emails):
            user, created = get_one_or_create(User, email=email)
            if created:
                new_users.append(user)
                team.users.append(user)
            elif user not in team.users:
                existing_users.append(user)
                team.users.append(user)
        return new_users, existing_users

    def _cleaned_emails(self, emails: str) -> Iterator[str]:
        email_list = emails.split("\n")  # TODO: very naive.
        for email in email_list:
            email = User.normalize_email(email)
            if User.validate_email(email) and User.validate_email_domain(
                email, self.request.registry.settings
            ):
                yield email

    def _send_new_users_invitations(self, users: List[User]) -> int:
        # TODO: async?
        mailer = get_mailer(self.request)
        subject = "Invitation à rejoindre un dossier législatif sur Zam"
        url = self.request.route_url("login")
        body = f"""
Bonjour,

Vous venez d’être invité·e à rejoindre Zam
pour participer au dossier législatif suivant :
{self.dossier.titre}

Veuillez vous connecter à Zam pour y accéder :
{url}

Bonne journée !
            """
        message = MailMessage(
            subject=subject,
            sender="contact@zam.beta.gouv.fr",
            recipients=[user.email for user in users],  # Is that a privacy issue?
            body=body.strip(),
        )
        mailer.send(message)
        return len(users)

    def _send_existing_users_invitations(self, users: List[User]) -> int:
        # TODO: async?
        mailer = get_mailer(self.request)
        subject = "Invitation à participer à un dossier législatif sur Zam"
        url = self.request.resource_url(self.request.context)
        body = f"""
Bonjour,

Vous venez d’être invité·e à participer
au dossier législatif suivant sur Zam :
{self.dossier.titre}

Vous pouvez y accéder via l’adresse suivante :
{url}

Bonne journée !
            """
        message = MailMessage(
            subject=subject,
            sender="contact@zam.beta.gouv.fr",
            recipients=[user.email for user in users],  # Is that a privacy issue?
            body=body.strip(),
        )
        mailer.send(message)
        return len(users)


@view_defaults(context=DossierResource, name="retrait", permission="retrait")
class DossierRetraitForm(DossierViewBase):
    @view_config(request_method="GET", renderer="dossier_retrait.html")
    def get(self) -> dict:
        return {
            "dossier": self.dossier,
            "dossier_resource": self.context,
            "current_tab": "retrait",
            "team": self.dossier.team,
            "current_user": self.request.user,
        }

    @view_config(request_method="POST")
    def post(self) -> Response:
        user_pk: str = self.request.POST.get("pk")
        user = DBSession.query(User).filter(User.pk == user_pk).one()
        target = str(user)

        self.dossier.team.users.remove(user)

        DossierRetrait.create(dossier=self.dossier, target=target, request=self.request)
        self.request.session.flash(
            Message(
                cls="success", text=(f"{target} a été retiré·e du dossier avec succès.")
            )
        )
        return HTTPFound(location=self.request.resource_url(self.context))


@view_config(context=DossierResource, name="journal", renderer="dossier_journal.html")
def lecture_journal(context: DossierResource, request: Request) -> Response:
    dossier = context.model()
    allowed_to_refresh = request.has_permission("refresh_dossier", context)
    return {
        "dossier": dossier,
        "dossier_resource": context,
        "today": date.today(),
        "current_tab": "journal",
        "allowed_to_refresh": allowed_to_refresh,
    }


@view_config(context=DossierResource, name="manual_refresh")
def manual_refresh(context: DossierResource, request: Request) -> Response:
    dossier = context.dossier
    update_dossier(dossier.pk, force=True)
    request.session.flash(
        Message(cls="success", text="Rafraichissement des lectures en cours.")
    )
    return HTTPFound(location=request.resource_url(context))
