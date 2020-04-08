from string import Template

from zam_repondeur.models.events.amendement import AmendementEvent


class AmendementSaisi(AmendementEvent):
    __mapper_args__ = {"polymorphic_identity": "amendement_saisi"}

    icon = "edit"

    summary_template = Template(
        f"L’amendement a été saisi par <abbr title='$email'>$user</abbr>."
    )

    def apply(self) -> None:
        pass

    def render_details(self) -> str:
        return ""
