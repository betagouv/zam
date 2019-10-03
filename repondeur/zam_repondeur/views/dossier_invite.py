from email.utils import formataddr
from typing import Iterator, List, Tuple

from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response
from pyramid.view import view_config, view_defaults
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message as MailMessage

from zam_repondeur.message import Message
from zam_repondeur.models import DBSession, Team, User, get_one_or_create
from zam_repondeur.models.events.dossier import DossierRetrait, InvitationEnvoyee
from zam_repondeur.resources import DossierResource

from .dossiers import DossierViewBase


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
                        "Aucune invitation n’a été envoyée, soit l’adresse courriel "
                        "saisie a déjà été destinataire d’une invitation, "
                        "soit il s’agit d’une adresse courriel non autorisée."
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
            if User.email_is_well_formed(email) and User.email_is_allowed(email):
                yield email

    def _send_new_users_invitations(self, users: List[User]) -> int:
        # TODO: async?
        mailer = get_mailer(self.request)
        reply_to = formataddr((self.request.user.name, self.request.user.email))
        subject = "Invitation à rejoindre un dossier législatif sur Zam"
        url = self.request.resource_url(self.request.context)
        body = f"""
Bonjour,

Vous venez d’être invité·e à rejoindre Zam
par {self.request.user}
pour participer au dossier législatif suivant :
{self.dossier.titre}

Vous pouvez y accéder via l’adresse suivante :
{url}

Bonne journée !
            """
        for user in users:
            message = MailMessage(
                subject=subject,
                sender="contact@zam.beta.gouv.fr",
                recipients=[user.email],
                body=body.strip(),
                extra_headers={"reply-to": reply_to},
            )
            mailer.send(message)
        return len(users)

    def _send_existing_users_invitations(self, users: List[User]) -> int:
        # TODO: async?
        mailer = get_mailer(self.request)
        reply_to = formataddr((self.request.user.name, self.request.user.email))
        subject = "Invitation à participer à un dossier législatif sur Zam"
        url = self.request.resource_url(self.request.context)
        body = f"""
Bonjour,

Vous venez d’être invité·e
par {self.request.user} à participer
au dossier législatif suivant sur Zam :
{self.dossier.titre}

Vous pouvez y accéder via l’adresse suivante :
{url}

Bonne journée !
            """
        for user in users:
            message = MailMessage(
                subject=subject,
                sender="contact@zam.beta.gouv.fr",
                recipients=[user.email],
                body=body.strip(),
                extra_headers={"reply-to": reply_to},
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
