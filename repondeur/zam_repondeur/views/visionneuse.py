from typing import Any, Dict, Tuple

from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config
from sqlalchemy.orm import joinedload, lazyload, load_only

from zam_repondeur.models import Article
from zam_repondeur.models.article import mult_key
from zam_repondeur.resources import ArticleCollection, ArticleResource


@view_config(context=ArticleCollection, renderer="visionneuse/articles.html")
def list_articles(context: ArticleCollection, request: Request) -> Dict[str, Any]:
    def _sort_key(item: Article) -> Tuple[int, str, Tuple[int, str], int]:
        """Custom sort: we want link related to `Titre` to be at the very end.

        This is because it is the correct order in the derouleur and thus
        it is discussed at the end of the seance.
        """
        return (
            Article._ORDER_TYPE[""]
            if item.type == "titre"
            else Article._ORDER_TYPE[item.type or ""],
            str(item.num or "").zfill(3),
            mult_key(item.mult or ""),
            Article._ORDER_POS[item.pos or ""],
        )

    lecture = context.lecture_resource.model(
        load_only("chambre", "dossier_pk", "organe", "partie", "texte_pk", "titre"),
        lazyload("articles").options(
            load_only("lecture_pk", "mult", "num", "pos", "type"),
            joinedload("user_content").load_only("title"),
        ),
        joinedload("texte").load_only("legislature", "numero"),
    )
    articles = sorted(lecture.articles, key=_sort_key)
    return {"lecture": lecture, "articles": articles}


@view_config(
    context=ArticleResource, name="reponses", renderer="visionneuse/reponses.html"
)
def list_reponses(context: ArticleResource, request: Request) -> Response:
    article = context.model(
        lazyload("amendements").options(
            load_only(
                "article_pk",
                "auteur",
                "corps",
                "expose",
                "groupe",
                "lecture_pk",
                "num",
                "parent_pk",
                "rectif",
                "sort",
            ),
            joinedload("user_content").load_only(
                "avis", "objet", "reponse", "has_objet", "has_reponse"
            ),
        ),
        lazyload("lecture").options(
            lazyload("amendements").options(
                load_only("article_pk", "auteur", "num", "rectif", "sort"),
                joinedload("user_content").load_only("avis"),
            ),
            joinedload("texte").load_only("legislature", "numero"),
            lazyload("articles").options(
                load_only("lecture_pk", "mult", "num", "pos", "type"),
            ),
        ),
    )
    return {
        "lecture": article.lecture,
        "article": article,
        "grouped_displayable_amendements": list(
            article.grouped_displayable_amendements()
        ),
        "next_article": article.next_article,
        "previous_article": article.previous_article,
    }
