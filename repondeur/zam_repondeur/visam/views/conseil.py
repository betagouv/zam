import logging
from collections import defaultdict
from datetime import date
from typing import Dict, List

from pyramid.httpexceptions import HTTPFound
from pyramid.request import Request
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
from zam_repondeur.visam.models.conseil import Formation
from zam_repondeur.visam.resources import ConseilResource

logger = logging.getLogger(__name__)


class ConseilViewBase:
    def __init__(self, context: ConseilResource, request: Request) -> None:
        self.context = context
        self.request = request


@view_defaults(context=ConseilResource)
class ConseilView(ConseilViewBase):
    @view_config(request_method="GET", renderer="conseil_item.html")
    def get(self) -> dict:
        conseil = self.context.model()
        lectures = conseil.lectures
        return {
            "conseil": conseil,
            "lectures": lectures,
            "current_tab": "conseils",
            "conseil_resource": self.context,
        }


@view_defaults(context=ConseilResource, name="add")
class TexteAddView(ConseilViewBase):
    @view_config(request_method="GET", renderer="texte_add.html")
    def get(self) -> dict:
        return {
            "current_tab": "conseils",
            "conseil_resource": self.context,
        }

    @view_config(request_method="POST")
    def post(self) -> Response:
        titre = self.request.POST["titre"]
        contenu = self.request.POST.get("contenu", "")

        conseil = self.context.model()
        texte = self.create_texte(conseil.chambre)
        dossier = self.create_dossier(titre)
        dossier.team = conseil.team

        lecture = self.create_lecture(texte, dossier, conseil.formation)
        conseil.lectures.append(lecture)

        self.create_articles(lecture, contenu)

        self.request.session.flash(
            Message(cls="success", text=("Texte créé avec succès."),)
        )
        location = self.request.resource_url(
            self.request.root["dossiers"][lecture.dossier.slug]["lectures"][
                lecture.url_key
            ]["amendements"]
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

    def create_dossier(self, titre: str) -> Dossier:
        slug = slugify(titre)
        dossier, _ = get_one_or_create(
            Dossier, slug=slug, create_kwargs={"titre": titre, "an_id": "dummy-" + slug}
        )
        return dossier

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
