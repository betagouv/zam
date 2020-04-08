from typing import Any, List, Optional, cast

from pyramid.request import Request
from pyramid.security import Allow, Authenticated, Deny, Everyone
from sqlalchemy import desc
from sqlalchemy.orm import Query

from zam_repondeur.menu import MenuAction
from zam_repondeur.models import DBSession, Dossier, Lecture, User
from zam_repondeur.resources import (
    ACE,
    AmendementCollection,
    ArticleCollection,
    DerouleurCollection,
    DossierResource,
    LectureResource,
    Resource,
    ResourceNotFound,
    Root,
    SharedTableCollection,
    TableCollection,
)

from .models.conseil import Conseil, ConseilLecture
from .models.events.members import MembersEvent


class VisamRoot(Root):
    """
    We create a special resource tree for Visam, with conseils instead of dossiers.
    """

    def __init__(self, _request: Request) -> None:
        super().__init__(_request)
        del self["dossiers"]
        self.add_child(ConseilCollection(name="conseils", parent=self))
        self.add_child(MembersCollection(name="members", parent=self))

    @property
    def default_child(self) -> Optional[Resource]:
        return cast(Resource, self["conseils"])

    class ManageMembers(MenuAction):
        title = "Gestion des membres"
        tab_name = "members"

        @property
        def should_show(self) -> bool:
            return self.request.has_permission("manage", self.resource["members"])

        @property
        def url(self) -> str:
            return self.request.resource_url(self.resource["members"])

    menu_actions = Root.menu_actions + [ManageMembers]


class ConseilCollection(Resource):
    __acl__ = [
        (Allow, "group:admins", "create_seance"),
        (Deny, Everyone, "create_seance"),
    ]

    def models(self, *options: Any) -> Query:
        result: Query = (
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
    def __acl__(self) -> List[ACE]:
        # Only chambre members and admins can view it.
        return [
            (Allow, "group:admins", "view"),
            (Allow, f"chambre:{self.model().chambre.name}", "view"),
            (Deny, Authenticated, "view"),
        ]

    def __init__(self, name: str, parent: Resource) -> None:
        super().__init__(name=name, parent=parent)
        self.slug = name
        self.add_child(TexteCollection(name="textes", parent=self))

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


class TexteCollection(Resource):
    @property
    def parent(self) -> ConseilResource:
        return cast(ConseilResource, self.__parent__)

    def __getitem__(self, key: str) -> Resource:
        return TexteResource(slug=key, parent=self)


class TexteResource(LectureResource):
    """
    We inherit from LectureResource in order to reuse the associated views
    """

    def __init__(self, slug: str, parent: Resource) -> None:
        Resource.__init__(self, name=slug, parent=parent)
        self.slug = slug
        self.add_child(AmendementCollection(name="amendements", parent=self))
        self.add_child(ArticleCollection(name="articles", parent=self))
        self.add_child(TableCollection(name="tables", parent=self))
        self.add_child(SharedTableCollection(name="boites", parent=self))
        self.add_child(DerouleurCollection(name="derouleur", parent=self))

    def model(self, *options: Any) -> Lecture:
        conseil = self.parent.parent.model()
        lecture: Optional[Lecture] = (
            DBSession.query(Lecture)
            .join(ConseilLecture)
            .join(Dossier)
            .filter(ConseilLecture.conseil_id == conseil.id, Dossier.slug == self.slug)
            .options(*options)
        ).one_or_none()
        if lecture is None:
            raise ResourceNotFound(self)
        return lecture

    @property
    def dossier_resource(self) -> Optional[DossierResource]:
        return None

    @property
    def breadcrumbs_label(self) -> Optional[str]:
        lecture: Lecture = self.model()
        return lecture.dossier.titre

    def back_resource(self, request: Request) -> Optional["Resource"]:
        conseil = self.parent.parent
        return conseil


class MembersCollection(Resource):
    __acl__ = [(Allow, "group:admins", "manage"), (Deny, Everyone, "manage")]

    def models(self, *options: Any) -> List[User]:
        result: List[User] = DBSession.query(User).options(*options)
        return result

    def events(self) -> Query:
        return DBSession.query(MembersEvent).order_by(desc(MembersEvent.created_at))
