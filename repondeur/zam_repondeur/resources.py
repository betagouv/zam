from itertools import chain
from typing import Any, Iterator, List, Optional, Tuple, Type, cast

from pyramid.httpexceptions import HTTPNotFound
from pyramid.request import Request
from pyramid.security import Allow, Authenticated, Deny, Everyone
from sqlalchemy import desc
from sqlalchemy.orm import Query, joinedload, lazyload, load_only, subqueryload
from sqlalchemy.orm.exc import NoResultFound

from zam_repondeur.decorator import reify
from zam_repondeur.menu import MenuAction
from zam_repondeur.models import (
    AllowedEmailPattern,
    Amendement,
    Article,
    Chambre,
    DBSession,
    Dossier,
    Lecture,
    SharedTable,
    User,
    UserTable,
)
from zam_repondeur.models.events.admin import AdminEvent
from zam_repondeur.models.events.whitelist import WhitelistEvent

# Access Control Entry (action, principal, permission)
ACE = Tuple[str, str, str]


class ResourceNotFound(HTTPNotFound):
    pass


class Resource(dict):
    """
    Location-aware resource

    See: https://docs.pylonsproject.org/projects/pyramid/en/latest/
    narr/resources.html#location-aware-resources
    """

    __name__: Optional[str] = None
    __parent__: Optional["Resource"] = None

    def __init__(self, name: str, parent: "Resource") -> None:
        self.__name__ = name
        self.__parent__ = parent

    @property
    def parent(self) -> Optional["Resource"]:
        return self.__parent__

    @property
    def parents(self) -> Iterator["Resource"]:
        parent = self.parent
        while parent is not None:
            yield parent
            parent = parent.parent

    @property
    def self_and_parents(self) -> Iterator["Resource"]:
        return chain([self], self.parents)

    def add_child(self, child: "Resource") -> None:
        self[child.__name__] = child

    def breadcrumbs(self, request: Request) -> Iterator["Resource"]:
        resources = list(reversed(list(self.parents)))
        resources.append(self)
        for resource in resources:
            if resource.breadcrumbs_label is not None:
                yield resource

    @property
    def breadcrumbs_label(self) -> Optional[str]:
        return None

    @property
    def breadcrumbs_class(self) -> str:
        return ""

    def back_url(self, request: Request) -> Optional[str]:
        # If we got there via URL dispatch, not traversal
        if getattr(request, "matched_route"):
            return request.resource_url(request.root.self_or_child())

        # If we're not on the resource's default view, go back to that
        if request.view_name != "":
            return request.resource_url(self.self_or_child())

        # Find a resource above this one
        resource = self.back_resource(request)
        if resource is None:
            return None
        resource = resource.self_or_child()
        if resource is self:
            return None
        return request.resource_url(resource)

    def back_resource(self, request: Request) -> Optional["Resource"]:
        return self.parent

    def self_or_child(self) -> "Resource":
        resource: "Resource" = self
        while resource.default_child is not None:
            resource = resource.default_child
        return resource

    @property
    def default_child(self) -> Optional["Resource"]:
        """Allows redirecting to a child for resources that don't have views"""
        return None

    @property
    def menu_actions(self) -> List[Type[MenuAction]]:
        return []


class Root(Resource):
    __acl__ = [
        (Allow, Authenticated, "view"),
        (Allow, "group:admins", "delete"),
        (Deny, Everyone, "delete"),
    ]

    def __init__(self, _request: Request) -> None:
        self.add_child(WhitelistCollection(name="whitelist", parent=self))
        self.add_child(AdminsCollection(name="admins", parent=self))
        self.add_child(DossierCollection(name="dossiers", parent=self))

    @property
    def default_child(self) -> Optional[Resource]:
        return cast(Resource, self["dossiers"])

    class ManageWhiteList(MenuAction):
        title = "Gestion des accès"
        tab_name = "whitelist"

        @property
        def should_show(self) -> bool:
            return self.request.has_permission("manage", self.resource["whitelist"])

        @property
        def url(self) -> str:
            return self.request.resource_url(self.resource["whitelist"])

    class ManageAdmins(MenuAction):
        title = "Gestion des administrateur·ice·s"
        tab_name = "admins"

        @property
        def should_show(self) -> bool:
            return self.request.has_permission("manage", self.resource["admins"])

        @property
        def url(self) -> str:
            return self.request.resource_url(self.resource["admins"])

    class EditProfile(MenuAction):
        link_class = "account"

        @property
        def title(self) -> str:
            return self.request.user.name or ""

        @property
        def should_show(self) -> bool:
            return bool(self.request.user.name)

        @property
        def url(self) -> str:
            return self.request.route_url("welcome")

    class Logout(MenuAction):
        title = "Déconnexion"
        link_class = "logout"

        @property
        def should_show(self) -> bool:
            return self.request.user is not None

        @property
        def url(self) -> str:
            return self.request.route_url("logout")

    menu_actions = [ManageWhiteList, ManageAdmins, EditProfile, Logout]


class WhitelistCollection(Resource):
    __acl__ = [(Allow, "group:admins", "manage"), (Deny, Everyone, "manage")]

    def models(self, *options: Any) -> List[AllowedEmailPattern]:
        result: List[AllowedEmailPattern] = DBSession.query(
            AllowedEmailPattern
        ).options(*options)
        return result

    def events(self) -> Query:
        return DBSession.query(WhitelistEvent).order_by(desc(WhitelistEvent.created_at))


class AdminsCollection(Resource):
    __acl__ = [(Allow, "group:admins", "manage"), (Deny, Everyone, "manage")]

    def models(self) -> List[User]:
        result: List[User] = DBSession.query(User).filter(
            User.admin_at.isnot(None)  # type: ignore
        )
        return result

    def events(self) -> Query:
        return DBSession.query(AdminEvent).order_by(desc(AdminEvent.created_at))


class DossierCollection(Resource):
    __acl__ = [(Allow, "group:admins", "activate"), (Deny, Everyone, "activate")]

    def models(self, *options: Any) -> List[Dossier]:
        result: List[Dossier] = DBSession.query(Dossier).options(*options)
        return result

    def __getitem__(self, key: str) -> Resource:
        resource = DossierResource(name=key, parent=self)
        try:
            resource.model()
        except ResourceNotFound:
            raise KeyError
        return resource


class DossierResource(Resource):
    def __acl__(self) -> List[ACE]:
        # Only team members and admins can view it.
        return [
            (Allow, f"group:admins", "view"),
            (Allow, f"team:{self.dossier.team.pk}", "view"),
            (Deny, Authenticated, "view"),
            (Allow, f"group:admins", "retrait"),
            (Deny, Authenticated, "retrait"),
            (Allow, "group:admins", "refresh"),
            (Deny, Everyone, "refresh"),
        ]

    def __init__(self, name: str, parent: Resource) -> None:
        super().__init__(name=name, parent=parent)
        self.slug = name
        self.add_child(LectureCollection(name="lectures", parent=self))

    @property
    def parent(self) -> DossierCollection:
        return cast(DossierCollection, self.__parent__)

    @reify
    def dossier(self) -> Dossier:
        return self.model(
            subqueryload("events").load_only("created_at"),
            lazyload("lectures").options(
                joinedload("texte"), lazyload("amendements").load_only("pk")
            ),
        )

    def model(self, *options: Any) -> Dossier:
        dossier = Dossier.get(self.slug, *options)
        if dossier is None:
            raise ResourceNotFound(self)
        return dossier

    breadcrumbs_class = "menu-dossier"

    @property
    def breadcrumbs_label(self) -> Optional[str]:
        dossier: Dossier = self.model()
        return dossier.titre

    class InviterAuDossier(MenuAction):
        title = "Inviter au dossier"
        tab_name = "invite"

        @property
        def url(self) -> str:
            return self.request.resource_url(self.resource, "invite")

    class RetirerAccesAuDossier(MenuAction):
        title = "Retirer l’accès au dossier"
        tab_name = "retrait"

        @property
        def should_show(self) -> bool:
            return self.request.has_permission("retrait", self.resource)

        @property
        def url(self) -> str:
            return self.request.resource_url(self.resource, "retrait")

    menu_actions = [InviterAuDossier, RetirerAccesAuDossier]


class LectureCollection(Resource):
    @property
    def parent(self) -> DossierResource:
        return cast(DossierResource, self.__parent__)

    def __getitem__(self, key: str) -> Resource:
        try:
            chambre, session_or_legislature, num_texte, organe = key.split(".")
            partie: Optional[int]
            if "-" in num_texte:
                num_texte, partie_str = num_texte.split("-", 1)
                partie = int(partie_str)
            else:
                partie = None
        except ValueError:
            raise KeyError
        return LectureResource(
            name=key,
            parent=self,
            chambre=chambre,
            session_or_legislature=session_or_legislature,
            num_texte=int(num_texte),
            partie=partie,
            organe=organe,
        )


class LectureResource(Resource):
    __acl__ = [
        (Allow, Authenticated, "refresh"),
        (Deny, Everyone, "refresh"),
    ]

    def __init__(
        self,
        name: str,
        parent: Resource,
        chambre: str,
        session_or_legislature: str,
        num_texte: int,
        partie: Optional[int],
        organe: str,
    ) -> None:
        super().__init__(name=name, parent=parent)
        self.chambre = Chambre.from_string(chambre)
        self.session_or_legislature = session_or_legislature
        self.num_texte = num_texte
        self.partie = partie
        self.organe = organe
        self.add_child(AmendementCollection(name="amendements", parent=self))
        self.add_child(ArticleCollection(name="articles", parent=self))
        self.add_child(TableCollection(name="tables", parent=self))
        self.add_child(SharedTableCollection(name="boites", parent=self))
        self.add_child(DerouleurCollection(name="derouleur", parent=self))

    @property
    def default_child(self) -> Resource:
        return cast(Resource, self["amendements"])

    @property
    def parent(self) -> LectureCollection:
        return cast(LectureCollection, self.__parent__)

    def back_resource(self, request: Request) -> Optional[Resource]:
        return self.dossier_resource

    @property
    def dossier_resource(self) -> DossierResource:
        return self.parent.parent

    @reify
    def lecture(self) -> Lecture:
        return self.model()

    def model(self, *options: Any) -> Lecture:
        lecture = Lecture.get(
            self.dossier_resource.dossier,
            self.chambre,
            self.session_or_legislature,
            self.num_texte,
            self.partie,
            self.organe,
            *options,
        )
        if lecture is None:
            raise ResourceNotFound(self)
        return lecture

    @property
    def breadcrumbs_label(self) -> Optional[str]:
        lecture = self.model()
        return (
            ", ".join(
                [
                    lecture.format_num_lecture(),
                    lecture.format_chambre(),
                    lecture.format_organe(),
                ]
            )
            + lecture.format_partie()
        )

    class DossierDeBanc(MenuAction):
        title = "Dossier de banc"
        open_in_new_window = True

        @property
        def url(self) -> str:
            return self.request.resource_url(self.resource["articles"])

    class OptionsAvancees(MenuAction):
        title = "Options avancées"
        tab_name = "options"

        @property
        def url(self) -> str:
            return self.request.resource_url(self.resource, "options")

    menu_actions = [DossierDeBanc, OptionsAvancees]


class AmendementCollection(Resource):
    def __getitem__(self, key: str) -> Resource:
        resource = AmendementResource(name=key, parent=self)
        if not resource.exists():
            raise KeyError
        return resource

    @property
    def parent(self) -> LectureResource:
        return cast(LectureResource, self.__parent__)

    def back_resource(self, request: Request) -> Optional[Resource]:
        return self.parent.back_resource(request)


class AmendementResource(Resource):
    def __init__(self, name: str, parent: Resource) -> None:
        super().__init__(name=name, parent=parent)
        self.num = name

    @property
    def parent(self) -> AmendementCollection:
        return cast(AmendementCollection, self.__parent__)

    @property
    def lecture_resource(self) -> LectureResource:
        return self.parent.parent

    def back_resource(self, request: Request) -> Optional[Resource]:
        return self.lecture_resource

    def model(self) -> Amendement:
        try:
            amendement: Amendement = (
                DBSession.query(Amendement)
                .filter_by(lecture=self.lecture_resource.model(), num=self.num)
                .options(joinedload("article"), joinedload("lecture"))
                .one()
            )
        except NoResultFound:
            raise ResourceNotFound(self)
        return amendement

    def exists(self) -> bool:
        return bool(
            DBSession.query(Amendement)
            .filter_by(lecture=self.lecture_resource.model(), num=self.num)
            .options(load_only("pk"))
            .one_or_none()
        )


class ArticleCollection(Resource):
    def __getitem__(self, key: str) -> Resource:
        try:
            type, num, mult, pos = key.split(".")
        except ValueError:
            raise KeyError
        return ArticleResource(key, self, type, num, mult, pos)

    @property
    def parent(self) -> LectureResource:
        return cast(LectureResource, self.__parent__)

    @property
    def lecture_resource(self) -> LectureResource:
        return self.parent


class ArticleResource(Resource):
    def __init__(
        self, name: str, parent: Resource, type: str, num: str, mult: str, pos: str
    ) -> None:
        super().__init__(name=name, parent=parent)
        self.type = type
        self.num = num
        self.mult = mult
        self.pos = pos

    @property
    def parent(self) -> ArticleCollection:
        return cast(ArticleCollection, self.__parent__)

    @property
    def lecture_resource(self) -> LectureResource:
        return self.parent.parent

    def back_resource(self, request: Request) -> Optional[Resource]:
        return self.lecture_resource

    def model(self, *options: Any) -> Article:
        lecture: Lecture = self.lecture_resource.model()
        try:
            article: Article = (
                DBSession.query(Article)
                .filter_by(
                    lecture=lecture,
                    type=self.type,
                    num=self.num,
                    mult=self.mult,
                    pos=self.pos,
                )
                .options(*options)
                .one()
            )
        except NoResultFound:
            raise ResourceNotFound(self)
        return article


class TableCollection(Resource):
    def __getitem__(self, key: str) -> Resource:
        return TableResource(name=key, parent=self)

    @property
    def parent(self) -> LectureResource:
        return cast(LectureResource, self.__parent__)


class TableResource(Resource):
    def __init__(self, name: str, parent: Resource) -> None:
        super().__init__(name=name, parent=parent)

    @property
    def parent(self) -> TableCollection:
        return cast(TableCollection, self.__parent__)

    def back_resource(self, request: Request) -> Optional[Resource]:
        return self.lecture_resource

    @property
    def lecture_resource(self) -> LectureResource:
        return self.parent.parent

    @property
    def owner(self) -> User:
        try:
            user: User = DBSession.query(User).filter(User.email == self.__name__).one()
            return user
        except NoResultFound:
            raise ResourceNotFound

    def model(self, options: Any = None) -> UserTable:
        return self.owner.table_for(
            lecture=self.lecture_resource.model(), options=options
        )


class SharedTableCollection(Resource):
    def __getitem__(self, key: str) -> Resource:
        if key == "add":
            raise KeyError
        return SharedTableResource(name=key, parent=self)

    @property
    def parent(self) -> LectureResource:
        return cast(LectureResource, self.__parent__)

    @property
    def lecture_resource(self) -> LectureResource:
        return self.parent


class SharedTableResource(Resource):
    def __init__(self, name: str, parent: Resource) -> None:
        super().__init__(name=name, parent=parent)
        self.add_child(SharedTableDeleteResource(name="delete", parent=self))

    @property
    def parent(self) -> SharedTableCollection:
        return cast(SharedTableCollection, self.__parent__)

    @property
    def lecture_resource(self) -> LectureResource:
        return self.parent.parent

    def model(self) -> SharedTable:
        try:
            shared_table: SharedTable = (
                DBSession.query(SharedTable)
                .filter(
                    SharedTable.slug == self.__name__,
                    SharedTable.lecture == self.lecture_resource.model(),
                )
                .one()
            )
        except NoResultFound:
            raise ResourceNotFound(self)
        return shared_table


class SharedTableDeleteResource(Resource):
    def __init__(self, name: str, parent: Resource) -> None:
        super().__init__(name=name, parent=parent)

    @property
    def parent(self) -> SharedTableResource:
        return cast(SharedTableResource, self.__parent__)

    @property
    def lecture_resource(self) -> LectureResource:
        return self.parent.parent.parent

    def model(self) -> SharedTable:
        return self.parent.model()


class DerouleurCollection(Resource):
    @property
    def parent(self) -> LectureResource:
        return cast(LectureResource, self.__parent__)

    @property
    def lecture_resource(self) -> LectureResource:
        return self.parent
