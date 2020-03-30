import logging
from collections import defaultdict
from datetime import date
from typing import Dict, List, Optional, Tuple

from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response
from pyramid.view import view_config, view_defaults
from selectolax.parser import HTMLParser
from sqlalchemy import func

from zam_repondeur.message import Message
from zam_repondeur.models import (
    Article,
    Chambre,
    DBSession,
    Dossier,
    Lecture,
    Phase,
    Texte,
    TypeTexte,
    get_one_or_create,
)
from zam_repondeur.models.events.lecture import LectureCreee
from zam_repondeur.services.clean import clean_html
from zam_repondeur.slugs import slugify
from zam_repondeur.visam.models.conseil import Conseil, Formation
from zam_repondeur.visam.resources import ConseilResource
from zam_repondeur.visam.views.conseil_item import ConseilViewBase

logger = logging.getLogger(__name__)


@view_defaults(context=ConseilResource, name="add")
class ConseilAddTexteView(ConseilViewBase):
    @view_config(request_method="GET", renderer="conseil_add_texte.html")
    def get(self) -> dict:
        return {
            "current_tab": "conseils",
            "conseil_resource": self.context,
        }

    @view_config(request_method="POST")
    def post(self) -> Response:
        titre = self.request.POST["titre"]
        contenu = self.request.POST.get("contenu", "")

        # Un même texte, ou des versions successives d’un même texte,
        # peuvent passer devant plusieurs conseils. Dans ce cas, les
        # lectures seront regroupées au sein d’un même dossier.
        dossier, created = self.find_or_create_dossier(titre, self.conseil.lectures)
        if created:
            dossier.team = self.conseil.team

        # Par contre, un même texte ne peut pas être examiné plusieurs
        # fois lors d’une même séance d’un conseil...
        lecture = self.find_lecture(dossier, self.conseil)
        if lecture is None:
            texte = self.create_texte(self.conseil.chambre)

            lecture = self.create_lecture(texte, dossier, self.conseil.formation)
            self.conseil.lectures.append(lecture)

            self.create_articles(lecture, contenu)

            self.request.session.flash(
                Message(cls="success", text="Texte créé avec succès.")
            )
        else:
            self.request.session.flash(
                Message(cls="warning", text="Ce texte existe déjà dans ce conseil…")
            )

        location = self.request.resource_url(
            self.context["textes"][lecture.dossier.slug]["amendements"]
        )
        return HTTPFound(location=location)

    def create_texte(self, chambre: Chambre) -> Texte:
        max_numero = (
            DBSession.query(func.max(Texte.numero))
            .filter(Texte.type_ == TypeTexte.PROJET, Texte.chambre == chambre)
            .scalar()
        ) or 0
        texte = Texte.create(
            type_=TypeTexte.PROJET,
            chambre=chambre,
            numero=max_numero + 1,
            date_depot=date.today(),
        )
        return texte

    def find_or_create_dossier(
        self, titre: str, lectures: List[Lecture]
    ) -> Tuple[Dossier, bool]:
        slug = slugify(titre)
        dossier, created = get_one_or_create(
            Dossier,
            slug=slug,
            create_kwargs={"titre": titre, "an_id": "dummy-" + slug},
        )
        return dossier, created

    def find_lecture(self, dossier: Dossier, conseil: Conseil) -> Optional[Lecture]:
        for lecture in conseil.lectures:
            if lecture.dossier is dossier:
                return lecture
        return None

    def create_lecture(
        self, texte: Texte, dossier: Dossier, formation: Formation
    ) -> Lecture:
        organe = formation.value
        lecture = Lecture.create(
            dossier=dossier,
            texte=texte,
            phase=Phase.PREMIERE_LECTURE,
            organe=organe,
            titre=f"Première lecture – {organe}",
        )
        LectureCreee.create(lecture=lecture, user=None)
        return lecture

    def create_articles(self, lecture: Lecture, contenu: str) -> None:
        for num, alineas in self.extract_articles(contenu).items():
            Article.create(
                type="article",
                num=num,
                mult="",
                pos="",
                lecture=lecture,
                content={
                    str(i).zfill(3): alinea for i, alinea in enumerate(alineas, start=1)
                },
            )

    def extract_articles(self, contenu: str) -> Dict[str, List[str]]:
        """
        Basic extraction of article contents

        Based on the following heuristics:
        - ignore everything before the first article
        - start a new article when a top-level element starts with "Article ..."
        - stop when a top-level element starts with "Fait le ..."
        """
        html = HTMLParser(clean_html(contenu))
        articles: Dict[str, List[str]] = defaultdict(list)
        current_article = None
        for node in html.css("body > *"):
            texte = node.text()
            if not texte.strip():  # skip empty lines
                continue
            if texte.startswith("Article "):
                current_article = texte[len("Article ") :]
            elif texte.startswith("Fait le "):  # beginning of boilerplate
                break
            elif current_article is not None:
                articles[current_article].append(node.html)
        return articles
