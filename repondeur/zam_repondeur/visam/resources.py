from typing import Any, List, Optional, cast

from pyramid.request import Request
from pyramid.security import Allow, Authenticated, Deny, Everyone
from sqlalchemy import desc
from sqlalchemy.orm import Query

from zam_repondeur.menu import MenuAction
from zam_repondeur.models import Chambre, DBSession, Dossier, Lecture, User
from zam_repondeur.resources import (
    ACE,
    AmendementCollection,
    ArticleCollection,
    DossierResource,
    LectureResource,
    Resource,
    ResourceNotFound,
    Root,
    SharedTableCollection,
    TableCollection,
)

from .models.events.membership import MembershipEvent
from .models.seance import Seance, SeanceLecture


class VisamRoot(Root):
    """
    We create a special resource tree for Visam, with seances instead of dossiers.
    """

    def __init__(self, _request: Request) -> None:
        super().__init__(_request)
        del self["dossiers"]
        self.add_child(SeanceCollection(name="seances", parent=self))
        self.add_child(MembersCollection(name="members", parent=self))

    @property
    def default_child(self) -> Optional[Resource]:
        return cast(Resource, self["seances"])

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


class SeanceCollection(Resource):
    __acl__ = [
        (Allow, "group:admins", "create_seance"),
        (Deny, Everyone, "create_seance"),
    ]

    def models(
        self, *options: Any, chambres: Optional[List[Chambre]] = None
    ) -> List[Seance]:
        query: Query = DBSession.query(Seance)
        if chambres:
            query = query.filter(Seance.chambre.in_(chambres))
        order_ = Seance.date.desc()  # type: ignore
        query = query.order_by(order_).options(*options)
        return cast(List[Seance], query.all())

    def __getitem__(self, key: str) -> Resource:
        resource = SeanceResource(name=key, parent=self)
        try:
            resource.model()
        except ResourceNotFound:
            raise KeyError
        return resource


class SeanceResource(Resource):
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
    def parent(self) -> SeanceCollection:
        return cast(SeanceCollection, self.__parent__)

    def model(self, *options: Any) -> Seance:
        seance = Seance.get(self.slug, *options)
        if seance is None:
            raise ResourceNotFound(self)
        return seance

    @property
    def breadcrumbs_label(self) -> Optional[str]:
        seance: Seance = self.model()
        return str(seance)


class TexteCollection(Resource):
    @property
    def parent(self) -> SeanceResource:
        return cast(SeanceResource, self.__parent__)

    def __getitem__(self, key: str) -> Resource:
        return TexteResource(slug=key, parent=self)


class TexteResource(LectureResource):
    """
    We inherit from LectureResource in order to reuse the associated views
    """

    def __init__(self, slug: str, parent: TexteCollection) -> None:
        Resource.__init__(self, name=slug, parent=parent)
        self.slug = slug
        self.add_child(AmendementCollection(name="amendements", parent=self))
        self.add_child(ArticleCollection(name="articles", parent=self))
        self.add_child(TableCollection(name="tables", parent=self))
        self.add_child(SharedTableCollection(name="boites", parent=self))
        self.add_child(DerouleurCollection(name="derouleur", parent=self))

    def model(self, *options: Any) -> Lecture:
        seance = self.parent.parent.model()
        lecture: Optional[Lecture] = (
            DBSession.query(Lecture)
            .join(SeanceLecture)
            .join(Dossier)
            .filter(SeanceLecture.seance_pk == seance.pk, Dossier.slug == self.slug)
            .options(*options)
        ).one_or_none()
        if lecture is None:
            raise ResourceNotFound(self)
        return lecture

    @property
    def parent(self) -> TexteCollection:
        return cast(TexteCollection, self.__parent__)

    @property
    def dossier_resource(self) -> Optional[DossierResource]:
        return None

    @property
    def seance_resource(self) -> SeanceResource:
        return self.parent.parent

    @property
    def breadcrumbs_label(self) -> Optional[str]:
        lecture: Lecture = self.model()
        return lecture.dossier.titre

    def back_resource(self, request: Request) -> Optional["Resource"]:
        return self.seance_resource


class MembersCollection(Resource):
    __acl__ = [(Allow, "group:admins", "manage"), (Deny, Everyone, "manage")]

    def models(self, *options: Any) -> List[User]:
        result: List[User] = DBSession.query(User).options(*options)
        return result

    def events(self) -> Query:
        return DBSession.query(MembershipEvent).order_by(
            desc(MembershipEvent.created_at)
        )


class DerouleurCollection(Resource):
    @property
    def parent(self) -> TexteResource:
        return cast(TexteResource, self.__parent__)

    @property
    def lecture_resource(self) -> LectureResource:
        return self.parent

    @property
    def texte_resource(self) -> TexteResource:
        return self.parent
