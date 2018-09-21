from pyramid.httpexceptions import HTTPFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config, view_defaults

from zam_repondeur.clean import clean_html
from zam_repondeur.message import Message
from zam_repondeur.models.visionneuse import build_tree
from zam_repondeur.resources import ArticleResource


@view_config(context=ArticleResource, name="reponses", renderer="visionneuse.html")
def list_reponses(context: ArticleResource, request: Request) -> Response:
    article = context.model()
    lecture = article.lecture
    amendements = lecture.amendements
    articles = build_tree(amendements, article)
    check_url = request.resource_path(context.parent.parent, "check")
    return {
        "dossier_legislatif": lecture.dossier_legislatif,
        "lecture": str(lecture),
        "articles": articles,
        "timestamp": lecture.modified_at_timestamp,
        "check_url": check_url,
        "current_article": article,
    }


@view_defaults(context=ArticleResource)
class ArticleEdit:
    def __init__(self, context: ArticleResource, request: Request) -> None:
        self.context = context
        self.request = request
        self.article = self.context.model()

    @view_config(request_method="GET", renderer="article_edit.html")
    def get(self) -> dict:
        lecture = self.context.lecture_resource.model()
        return {"article": self.article, "lecture": lecture}

    @view_config(request_method="POST")
    def post(self) -> Response:
        self.article.titre = self.request.POST["titre"]
        self.article.jaune = clean_html(self.request.POST["jaune"])
        self.request.session.flash(
            Message(cls="success", text="Article mis à jour avec succès.")
        )
        resource = self.context.lecture_resource["amendements"]
        return HTTPFound(location=self.request.resource_url(resource))
