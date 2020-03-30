from pyramid.view import view_config, view_defaults

from zam_repondeur.models import Lecture
from zam_repondeur.visam.resources import ConseilResource
from zam_repondeur.visam.views.conseil_item import ConseilViewBase


@view_defaults(context=ConseilResource, name="order")
class ConseilReorderTextesView(ConseilViewBase):
    @view_config(request_method="POST", renderer="json")
    def post(self) -> dict:
        ordered_lecture_pks = (int(pk) for pk in self.request.json_body["order"])
        ordered_lectures = (Lecture.get_by_pk(pk) for pk in ordered_lecture_pks)
        self.conseil.lectures = [
            lecture for lecture in ordered_lectures if lecture is not None
        ]
        return {}
