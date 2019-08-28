from string import Template
from typing import Any, List, Optional

from jinja2 import Markup
from lxml.html.diff import htmldiff  # nosec
from pyramid.request import Request

from zam_repondeur.views.jinja2_filters import enumeration

from ..amendement import Amendement, Batch
from ..chambre import Chambre
from .base import Event


class AmendementEvent(Event):
    icon = ""

    summary_template = Template("<abbr title='$email'>$user</abbr>")

    def __init__(
        self, amendement: Amendement, request: Optional[Request] = None, **kwargs: Any
    ):
        super().__init__(request=request, **kwargs)
        self.amendement = amendement

    @property
    def template_vars(self) -> dict:
        template_vars = {
            "new_value": self.data["new_value"],
            "old_value": self.data["old_value"],
        }
        if self.user:
            template_vars.update({"user": self.user.name, "email": self.user.email})
        return template_vars

    def render_summary(self) -> str:
        return Markup(self.summary_template.safe_substitute(**self.template_vars))

    def render_details(self) -> str:
        return Markup(
            htmldiff(self.template_vars["old_value"], self.template_vars["new_value"])
        )


class AmendementRectifie(AmendementEvent):
    __mapper_args__ = {"polymorphic_identity": "amendement_rectifie"}

    icon = "edit"

    summary_template = Template("L’amendement a été rectifié.")

    def __init__(self, amendement: Amendement, rectif: str) -> None:
        super().__init__(
            amendement=amendement, old_value=amendement.rectif, new_value=rectif
        )

    def apply(self) -> None:
        self.amendement.rectif = self.data["new_value"]

    def render_details(self) -> str:
        return ""


class AmendementIrrecevable(AmendementEvent):
    __mapper_args__ = {"polymorphic_identity": "amendement_irrecevable"}

    icon = "document"

    @property
    def summary_template(self) -> Template:  # type: ignore
        chambre = self.amendement.lecture.chambre
        if chambre == Chambre.AN:
            de_qui = "de l’Asssemblée nationale"
        elif chambre == Chambre.SENAT:
            de_qui = "du Sénat"
        else:
            raise ValueError(f"Unsupported chambre {chambre}")
        return Template(
            f"L’amendement a été déclaré irrecevable par les services {de_qui}."
        )

    def __init__(self, amendement: Amendement, sort: str) -> None:
        super().__init__(
            amendement=amendement, old_value=amendement.sort, new_value=sort
        )

    def apply(self) -> None:
        self.amendement.sort = self.data["new_value"]

    def render_details(self) -> str:
        return ""


class AmendementTransfere(AmendementEvent):
    __mapper_args__ = {"polymorphic_identity": "amendement_transfere"}

    icon = "boite"

    @property
    def summary_template(self) -> Template:  # type: ignore
        if self.template_vars["old_value"] and self.template_vars["new_value"]:
            if str(self.user) == self.template_vars["old_value"]:
                summary = (
                    "<abbr title='$email'>$user</abbr> a transféré l’amendement "
                    "à « $new_value »."
                )
            elif str(self.user) == self.template_vars["new_value"]:
                summary = (
                    "<abbr title='$email'>$user</abbr> a transféré l’amendement "
                    "de « $old_value » à lui/elle-même."
                )
            else:
                summary = (
                    "<abbr title='$email'>$user</abbr> a transféré l’amendement "
                    "de « $old_value » à « $new_value »."
                )
        elif self.template_vars["old_value"] and not self.template_vars["new_value"]:
            if self.user:
                if str(self.user) == self.template_vars["old_value"]:
                    summary = (
                        "<abbr title='$email'>$user</abbr> a remis l’amendement "
                        "dans l’index."
                    )
                else:
                    summary = (
                        "<abbr title='$email'>$user</abbr> a remis l’amendement "
                        "de « $old_value » dans l’index."
                    )
            else:
                summary = "L’amendement a été remis automatiquement sur l’index."
        else:
            if str(self.user) == self.template_vars["new_value"]:
                summary = (
                    "<abbr title='$email'>$user</abbr> a mis l’amendement "
                    "sur sa table."
                )
            else:
                summary = (
                    "<abbr title='$email'>$user</abbr> a transféré l’amendement "
                    "à « $new_value »."
                )
        return Template(summary)

    def __init__(
        self,
        amendement: Amendement,
        old_value: str,
        new_value: str,
        request: Optional[Request] = None,
    ) -> None:
        super().__init__(
            amendement=amendement,
            old_value=old_value,
            new_value=new_value,
            request=request,
        )

    def apply(self) -> None:
        pass

    def render_details(self) -> str:
        return ""


class CorpsAmendementModifie(AmendementEvent):
    __mapper_args__ = {"polymorphic_identity": "corps_amendement_modifie"}

    icon = "edit"

    def __init__(self, amendement: Amendement, corps: str) -> None:
        super().__init__(
            amendement=amendement, old_value=amendement.corps or "", new_value=corps
        )

    @property
    def summary_template(self) -> Template:  # type: ignore
        action = "modifié" if self.template_vars["old_value"] else "initialisé"
        return Template(f"Le corps de l’amendement a été {action}.")

    def apply(self) -> None:
        self.amendement.corps = self.data["new_value"]


class ExposeAmendementModifie(AmendementEvent):
    __mapper_args__ = {"polymorphic_identity": "expose_amendement_modifie"}
    icon = "edit"

    def __init__(self, amendement: Amendement, expose: str) -> None:
        super().__init__(
            amendement=amendement, old_value=amendement.expose or "", new_value=expose
        )

    @property
    def summary_template(self) -> Template:  # type: ignore
        action = "modifié" if self.template_vars["old_value"] else "initialisé"
        return Template(f"L’exposé de l’amendement a été {action}.")

    def apply(self) -> None:
        self.amendement.expose = self.data["new_value"]


class AvisAmendementModifie(AmendementEvent):
    __mapper_args__ = {"polymorphic_identity": "avis_amendement_modifie"}

    icon = "edit"

    def __init__(
        self, amendement: Amendement, avis: str, request: Optional[Request] = None
    ) -> None:
        super().__init__(
            amendement=amendement,
            old_value=amendement.user_content.avis or "",
            new_value=avis,
            request=request,
        )

    def apply(self) -> None:
        self.amendement.user_content.avis = self.data["new_value"]

    @property
    def summary_template(self) -> Template:  # type: ignore
        if self.template_vars["old_value"]:
            summary = (
                "<abbr title='$email'>$user</abbr> a modifié l’avis "
                "de « $old_value » à « $new_value »."
            )
        else:
            summary = "<abbr title='$email'>$user</abbr> a mis l’avis à « $new_value »."
        return Template(summary)

    def render_details(self) -> str:
        return ""


class ObjetAmendementModifie(AmendementEvent):
    __mapper_args__ = {"polymorphic_identity": "objet_modifie"}

    icon = "edit"

    def __init__(
        self, amendement: Amendement, objet: str, request: Optional[Request] = None
    ) -> None:
        super().__init__(
            amendement=amendement,
            old_value=amendement.user_content.objet or "",
            new_value=objet,
            request=request,
        )

    @property
    def summary_template(self) -> Template:  # type: ignore
        action = "modifié" if self.template_vars["old_value"] else "ajouté"
        return Template(f"<abbr title='$email'>$user</abbr> a {action} l’objet.")

    def apply(self) -> None:
        self.amendement.user_content.objet = self.data["new_value"]


class ReponseAmendementModifiee(AmendementEvent):
    __mapper_args__ = {"polymorphic_identity": "reponse_amendement_modifiee"}

    icon = "edit"

    def __init__(
        self, amendement: Amendement, reponse: str, request: Optional[Request] = None
    ) -> None:
        super().__init__(
            amendement=amendement,
            old_value=amendement.user_content.reponse or "",
            new_value=reponse,
            request=request,
        )

    @property
    def summary_template(self) -> Template:  # type: ignore
        action = "modifié" if self.template_vars["old_value"] else "ajouté"
        return Template(f"<abbr title='$email'>$user</abbr> a {action} la réponse.")

    def apply(self) -> None:
        self.amendement.user_content.reponse = self.data["new_value"]


class CommentsAmendementModifie(AmendementEvent):
    __mapper_args__ = {"polymorphic_identity": "comments_amendement_modifie"}

    icon = "edit"

    def __init__(
        self, amendement: Amendement, comments: str, request: Optional[Request] = None
    ) -> None:
        super().__init__(
            amendement=amendement,
            old_value=amendement.user_content.comments or "",
            new_value=comments,
            request=request,
        )

    @property
    def summary_template(self) -> Template:  # type: ignore
        action = "modifié les" if self.template_vars["old_value"] else "ajouté des"
        return Template(f"<abbr title='$email'>$user</abbr> a {action} commentaires.")

    def apply(self) -> None:
        self.amendement.user_content.comments = self.data["new_value"]


class BatchSet(AmendementEvent):
    __mapper_args__ = {"polymorphic_identity": "batch_set"}

    icon = "edit"

    def __init__(
        self,
        amendement: Amendement,
        batch: Batch,
        amendements_nums: List[int],
        request: Request,
    ) -> None:
        self.request = request
        others = [
            amendement_num
            for amendement_num in amendements_nums
            if int(amendement_num) != amendement.num
        ]
        super().__init__(
            amendement=amendement, amendements_nums=others, request=request
        )
        self.batch = batch

    def apply(self) -> None:
        if self.amendement.batch:
            BatchUnset.create(amendement=self.amendement, request=self.request)
        self.amendement.batch = self.batch

    def render_details(self) -> str:
        return ""

    def render_summary(self) -> str:
        nums = self.data["amendements_nums"]
        if len(nums) == 1:
            siblings = f"l’amendement {nums[0]}"
        else:
            siblings = f"les amendements {enumeration(nums)}"
        return Markup(
            f"<abbr title='{self.user.email}'>{self.user.name}</abbr> a placé "
            f"cet amendement dans un lot avec {siblings}."
        )


class BatchUnset(AmendementEvent):
    __mapper_args__ = {"polymorphic_identity": "batch_unset"}

    icon = "edit"

    def __init__(self, amendement: Amendement, request: Request) -> None:
        self.request = request
        super().__init__(amendement=amendement, request=request)

    def apply(self) -> None:
        batch = self.amendement.batch
        if batch is None:
            return

        others = [amdt for amdt in batch.amendements if amdt is not self.amendement]

        # Remove amendement from batch.
        self.amendement.batch = None

        # Avoid lonely amendement in a batch.
        if len(others) == 1:
            self.create(amendement=others[0], request=self.request)

    def render_details(self) -> str:
        return ""

    def render_summary(self) -> str:
        return Markup(
            f"<abbr title='{self.user.email}'>{self.user.name}</abbr> a sorti "
            "cet amendement du lot dans lequel il était."
        )
