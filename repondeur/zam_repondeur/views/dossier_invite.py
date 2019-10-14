from email.utils import formataddr
from typing import Iterable, Iterator, List, Tuple

from more_itertools import partition, unique_everseen
from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response
from pyramid.view import view_config, view_defaults
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message as MailMessage

from zam_repondeur.message import Message
from zam_repondeur.models import DBSession, Team, User, get_one_or_create
from zam_repondeur.models.events.dossier import DossierRetrait, InvitationEnvoyee
from zam_repondeur.resources import DossierResource
from zam_repondeur.views.jinja2_filters import enumeration

from .dossier import DossierViewBase


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

        # Only consider well formed addresses from allowed domains
        emails = self._extract_emails(self.request.POST.get("emails"))
        bad_emails, clean_emails = self._clean_emails(emails)

        # Create user accounts if needed
        new_users, existing_users = self._find_or_create_users(clean_emails)

        team = self.dossier.team

        # Users that already have a Zam account, but are not yet members
        new_members, existing_members = self._identify_members(existing_users, team)

        users_to_invite = new_users + new_members

        team.add_members(users_to_invite)

        invitations_sent = 0
        if new_users:
            invitations_sent += self._send_new_users_invitations(new_users)
        if new_members:
            invitations_sent += self._send_existing_users_invitations(new_members)

        for user in users_to_invite:
            InvitationEnvoyee.create(
                dossier=self.dossier, email=user.email, request=self.request
            )

        if invitations_sent:
            if invitations_sent > 1:
                message = "Invitations envoyées avec succès."
            else:
                message = "Invitation envoyée avec succès."
            cls = "success"
        else:
            message = "Aucune invitation n’a été envoyée."
            cls = "warning"

        if existing_members:
            existing_emails = [user.email for user in existing_members]
            message += "<br><br>"
            if len(existing_emails) > 1:
                message += (
                    f"Les adresses courriel {enumeration(existing_emails)} "
                    "avaient déjà été invitées au dossier précédemment."
                )
            else:
                message += (
                    f"L’adresse courriel {existing_emails[0]} "
                    "avait déjà été invitée au dossier précédemment."
                )

        if bad_emails:
            message += "<br><br>"
            if len(bad_emails) > 1:
                message += (
                    f"Les adresses courriel {enumeration(bad_emails)} "
                    "sont mal formées ou non autorisées et n’ont pas été invitées."
                )
            else:
                message += (
                    f"L’adresse courriel {bad_emails[0]} "
                    "est mal formée ou non autorisée et n’a pas été invitée."
                )

        self.request.session.flash(Message(cls=cls, text=message))

        return HTTPFound(location=self.request.resource_url(self.context))

    def _extract_emails(self, text: str) -> Iterator[str]:
        emails = (line.strip() for line in text.split("\n"))  # TODO: very naive.
        non_empty_emails = (email for email in emails if email != "")
        unique_emails: Iterator[str] = unique_everseen(non_empty_emails)
        return unique_emails

    def _clean_emails(self, emails: Iterable[str]) -> Tuple[List[str], List[str]]:
        normalized_emails = (User.normalize_email(email) for email in emails)
        bad_emails, clean_emails = partition(self._is_email_valid, normalized_emails)
        return list(bad_emails), list(clean_emails)

    @staticmethod
    def _is_email_valid(email: str) -> bool:
        return User.email_is_well_formed(email) and User.email_is_allowed(email)

    def _find_or_create_users(self, emails: List[str]) -> Tuple[List[User], List[User]]:
        new_users = []
        existing_users = []
        for email in emails:
            user, created = get_one_or_create(User, email=email)
            if created:
                new_users.append(user)
            else:
                existing_users.append(user)
        return new_users, existing_users

    def _identify_members(
        self, users: List[User], team: Team
    ) -> Tuple[List[User], List[User]]:
        not_members, members = partition(team.is_member, users)
        return list(not_members), list(members)

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
        return HTTPFound(location=self.request.resource_url(self.context, "retrait"))
