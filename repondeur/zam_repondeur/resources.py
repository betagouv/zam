from typing import Iterator, List, Optional, cast

from pyramid.request import Request
from sqlalchemy.orm.exc import NoResultFound

from zam_repondeur.models import Amendement, Article, DBSession, Lecture


class ResourceNotFound(Exception):
    pass


class Resource(dict):
    """
    Location-aware resource

    See: https://docs.pylonsproject.org/projects/pyramid/en/latest/
    narr/resources.html#location-aware-resources
    """

    __name__: Optional[str] = None
    __parent__: Optional["Resource"] = None

    @property
    def breadcrumbs_title(self) -> str:
        raise NotImplementedError  # pragma: no cover

    breadcrumbs_link: bool = True

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
    def ancestors(self) -> List["Resource"]:
        return list(reversed(list(self.parents)))

    def add_child(self, child: "Resource") -> None:
        self[child.__name__] = child


class Root(Resource):
    def __init__(self, request: Request) -> None:
        self.add_child(LectureCollection(name="lectures", parent=self))


class LectureCollection(Resource):

    breadcrumbs_title = "Lectures"

    def models(self) -> List[Lecture]:
        return Lecture.all()

    def __getitem__(self, key: str) -> Resource:
        try:
            chambre, session, num_texte, organe = key.split(".")
        except ValueError:
            raise KeyError
        return LectureResource(
            name=key,
            parent=self,
            chambre=chambre,
            session=session,
            num_texte=int(num_texte),
            organe=organe,
        )


class LectureResource(Resource):
    def __init__(
        self,
        name: str,
        parent: Resource,
        chambre: str,
        session: str,
        num_texte: int,
        organe: str,
    ) -> None:
        super().__init__(name=name, parent=parent)
        self.chambre = chambre
        self.session = session
        self.num_texte = num_texte
        self.organe = organe
        self.add_child(AmendementCollection(name="amendements", parent=self))
        self.add_child(ArticleCollection(name="articles", parent=self))

    def model(self) -> Lecture:
        lecture = Lecture.get(self.chambre, self.session, self.num_texte, self.organe)
        if lecture is None:
            raise ResourceNotFound(self)
        return lecture

    @property
    def breadcrumbs_title(self) -> str:
        return f"{self.model().dossier_legislatif} → {str(self.model())}"


class AmendementCollection(Resource):

    breadcrumbs_title = "Amendements"

    def __getitem__(self, key: str) -> Resource:
        return AmendementResource(name=key, parent=self)

    @property
    def parent(self) -> LectureResource:
        return cast(LectureResource, self.__parent__)


class AmendementResource(Resource):

    breadcrumbs_link = False

    def __init__(self, name: str, parent: Resource) -> None:
        super().__init__(name=name, parent=parent)
        self.num = int(name)

    @property
    def parent(self) -> AmendementCollection:
        return cast(AmendementCollection, self.__parent__)

    @property
    def lecture_resource(self) -> LectureResource:
        return self.parent.parent

    def model(self) -> Amendement:
        try:
            amendement: Amendement = (
                DBSession.query(Amendement)
                .filter_by(lecture=self.lecture_resource.model(), num=self.num)
                .one()
            )
        except NoResultFound:
            raise ResourceNotFound(self)
        return amendement

    @property
    def breadcrumbs_title(self) -> str:
        amendement = self.model()
        return amendement.num_disp


class ArticleCollection(Resource):

    breadcrumbs_title = "Articles"
    breadcrumbs_link = False

    def __getitem__(self, key: str) -> Resource:
        try:
            type, num, mult, pos = key.split(".")
        except ValueError:
            raise KeyError
        return ArticleResource(key, self, type, num, mult, pos)

    @property
    def parent(self) -> LectureResource:
        return cast(LectureResource, self.__parent__)


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

    def model(self) -> Article:
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
                .one()
            )
        except NoResultFound:
            raise ResourceNotFound(self)
        return article

    @property
    def breadcrumbs_title(self) -> str:
        type_ = self.type == "article" and "art." or self.type
        text = f"{self.pos} {type_} {self.num} {self.mult}"
        return text.strip().capitalize()
