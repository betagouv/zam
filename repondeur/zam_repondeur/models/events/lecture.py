from string import Template
from typing import Any

from jinja2 import Markup
from pyramid.request import Request
from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import backref, relationship

from ..lecture import Lecture
from .base import Event


class LectureEvent(Event):
    lecture_pk = Column(Integer, ForeignKey("lectures.pk"))
    lecture = relationship(
        Lecture, backref=backref("events", order_by="Event.created_at.desc()")
    )

    details_template = Template("")

    def __init__(self, request: Request, lecture: Lecture, **kwargs: Any):
        super().__init__(request, **kwargs)
        self.lecture = lecture

    @property
    def template_vars(self) -> dict:
        if self.user:
            return {"user": self.user.name, "email": self.user.email}
        return {}

    def render_summary(self) -> str:
        return Markup(self.summary_template.safe_substitute(**self.template_vars))

    def render_details(self) -> str:
        return Markup(self.details_template.safe_substitute(**self.template_vars))


class LectureCreee(LectureEvent):
    __mapper_args__ = {"polymorphic_identity": "lecture_creee"}
    icon = "document"

    summary_template = Template("<abbr title='$email'>$user</abbr> a créé la lecture.")

    def __init__(self, request: Request, lecture: Lecture, **kwargs: Any) -> None:
        super().__init__(request, lecture, **kwargs)

    def apply(self) -> None:
        pass


class ArticlesRecuperes(LectureEvent):
    __mapper_args__ = {"polymorphic_identity": "articles_recuperes"}
    icon = "document"

    summary_template = Template("Le contenu des articles a été récupéré.")

    def __init__(self, request: Request, lecture: Lecture, **kwargs: Any) -> None:
        super().__init__(request, lecture, **kwargs)

    def apply(self) -> None:
        pass


class AmendementsRecuperes(LectureEvent):
    __mapper_args__ = {"polymorphic_identity": "amendements_recuperes"}
    icon = "document"

    @property
    def summary_template(self) -> Template:
        count = self.data["count"]
        if count == 1:
            message = "1 nouvel amendement récupéré."
        else:
            message = f"{count} nouveaux amendements récupérés."
        return Template(message)

    def __init__(self, request: Request, lecture: Lecture, **kwargs: Any) -> None:
        super().__init__(request, lecture, **kwargs)

    def apply(self) -> None:
        pass


class AmendementsRecuperesLiasse(LectureEvent):
    __mapper_args__ = {"polymorphic_identity": "amendements_recuperes_liasse"}
    icon = "document"

    @property
    def summary_template(self) -> Template:
        count = self.data["count"]
        base = "<abbr title='$email'>$user</abbr> a importé une liasse XML"
        if count == 1:
            message = "1 nouvel amendement récupéré."
        else:
            message = f"{count} nouveaux amendements récupérés."
        return Template(f"{base} : {message}")

    def __init__(self, request: Request, lecture: Lecture, **kwargs: Any) -> None:
        super().__init__(request, lecture, **kwargs)

    def apply(self) -> None:
        pass


class AmendementsNonRecuperes(LectureEvent):
    __mapper_args__ = {"polymorphic_identity": "amendements_non_recuperes"}
    icon = "document"

    @property
    def summary_template(self) -> Template:
        missings = ", ".join(self.data["missings"])
        return Template(f"Les amendements {missings} n’ont pu être récupérés.")

    def __init__(self, request: Request, lecture: Lecture, **kwargs: Any) -> None:
        super().__init__(request, lecture, **kwargs)

    def apply(self) -> None:
        pass


class AmendementsAJour(LectureEvent):
    __mapper_args__ = {"polymorphic_identity": "amendements_a_jour"}
    icon = "document"

    summary_template = Template("Les amendements étaient à jour.")

    def __init__(self, request: Request, lecture: Lecture, **kwargs: Any) -> None:
        super().__init__(request, lecture, **kwargs)

    def apply(self) -> None:
        pass


class AmendementsNonTrouves(LectureEvent):
    __mapper_args__ = {"polymorphic_identity": "amendements_non_trouves"}
    icon = "document"

    summary_template = Template("Les amendements n’ont pas été trouvés.")

    def __init__(self, request: Request, lecture: Lecture, **kwargs: Any) -> None:
        super().__init__(request, lecture, **kwargs)

    def apply(self) -> None:
        pass


class ReponsesImportees(LectureEvent):
    __mapper_args__ = {"polymorphic_identity": "reponses_importees"}
    icon = "document"

    summary_template = Template(
        "<abbr title='$email'>$user</abbr> a importé des réponses d’un fichier CSV."
    )

    def __init__(self, request: Request, lecture: Lecture, **kwargs: Any) -> None:
        super().__init__(request, lecture, **kwargs)

    def apply(self) -> None:
        pass


class ReponsesImporteesJSON(LectureEvent):
    __mapper_args__ = {"polymorphic_identity": "reponses_importees_json"}
    icon = "document"

    summary_template = Template(
        "<abbr title='$email'>$user</abbr> a importé des réponses d’un fichier JSON."
    )

    def __init__(self, request: Request, lecture: Lecture, **kwargs: Any) -> None:
        super().__init__(request, lecture, **kwargs)

    def apply(self) -> None:
        pass


class SharedTableCreee(LectureEvent):
    __mapper_args__ = {"polymorphic_identity": "shared_table_creee"}
    icon = "document"

    @property
    def summary_template(self) -> Template:
        titre = self.data["titre"]
        return Template(
            f"<abbr title='$email'>$user</abbr> a créé la boîte « {titre} »"
        )

    def __init__(self, request: Request, lecture: Lecture, **kwargs: Any) -> None:
        super().__init__(request, lecture, **kwargs)

    def apply(self) -> None:
        pass


class SharedTableRenommee(LectureEvent):
    __mapper_args__ = {"polymorphic_identity": "shared_table_renommee"}
    icon = "document"

    @property
    def summary_template(self) -> Template:
        old_titre = self.data["old_titre"]
        new_titre = self.data["new_titre"]
        return Template(
            f"<abbr title='$email'>$user</abbr> a renommé la boîte "
            f"« {old_titre} » en « {new_titre} »"
        )

    def __init__(self, request: Request, lecture: Lecture, **kwargs: Any) -> None:
        super().__init__(request, lecture, **kwargs)

    def apply(self) -> None:
        pass


class SharedTableSupprimee(LectureEvent):
    __mapper_args__ = {"polymorphic_identity": "shared_table_supprimee"}
    icon = "document"

    @property
    def summary_template(self) -> Template:
        titre = self.data["titre"]
        return Template(
            f"<abbr title='$email'>$user</abbr> a supprimé la boîte « {titre} »"
        )

    def __init__(self, request: Request, lecture: Lecture, **kwargs: Any) -> None:
        super().__init__(request, lecture, **kwargs)

    def apply(self) -> None:
        pass
