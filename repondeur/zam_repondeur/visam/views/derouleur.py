from typing import Any, Dict

from pyramid.request import Request
from pyramid.view import view_config
from sqlalchemy.orm import joinedload, load_only

from zam_repondeur.visam.resources import DerouleurCollection


@view_config(context=DerouleurCollection, renderer="derouleur.html")
def derouleur(context: DerouleurCollection, request: Request) -> Dict[str, Any]:
    lecture = context.lecture_resource.model(
        load_only(
            "chambre", "dossier_pk", "organe", "partie", "texte_pk", "titre", "phase"
        ),
        joinedload("articles").options(
            load_only("lecture_pk", "mult", "num", "pos", "type", "content"),
            joinedload("user_content").load_only("title", "presentation"),
            joinedload("amendements"),
        ),
        joinedload("texte").load_only("legislature", "numero"),
    )
    articles = sorted(lecture.articles)
    return {
        "lecture": lecture,
        "articles": articles,
    }
