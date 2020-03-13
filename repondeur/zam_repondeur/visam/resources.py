from typing import Any, List, Optional, cast

from pyramid.request import Request
from pyramid.security import Allow, Deny, Everyone

from zam_repondeur.models import Conseil, DBSession
from zam_repondeur.resources import Resource, ResourceNotFound, Root


class VisamRoot(Root):
    def __init__(self, _request: Request) -> None:
        super().__init__(_request)
        self.add_child(ConseilCollection(name="conseils", parent=self))

    @property
    def default_child(self) -> Optional[Resource]:
        return cast(Resource, self["conseils"])


class ConseilCollection(Resource):
    __acl__ = [(Allow, "group:admins", "add"), (Deny, Everyone, "add")]

    def models(self, *options: Any) -> List[Conseil]:
        result: List[Conseil] = (
            DBSession.query(Conseil).order_by(Conseil.date.desc()).options(*options)
        )
        return result

    def __getitem__(self, key: str) -> Resource:
        resource = ConseilResource(name=key, parent=self)
        try:
            resource.model()
        except ResourceNotFound:
            raise KeyError
        return resource


class ConseilResource(Resource):
    def __init__(self, name: str, parent: Resource) -> None:
        super().__init__(name=name, parent=parent)
        self.slug = name

    @property
    def parent(self) -> ConseilCollection:
        return cast(ConseilCollection, self.__parent__)

    def model(self, *options: Any) -> Conseil:
        conseil = Conseil.get(self.slug, *options)
        if conseil is None:
            raise ResourceNotFound(self)
        return conseil

    @property
    def breadcrumbs_label(self) -> Optional[str]:
        conseil: Conseil = self.model()
        return str(conseil)
