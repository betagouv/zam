from typing import List, Optional

from pyramid.request import Request

from zam_repondeur.models import (
    Amendement as AmendementModel,
    Lecture as LectureModel,
    DBSession,
)


class Resource(dict):
    """
    Location-aware resource

    See: https://docs.pylonsproject.org/projects/pyramid/en/latest/narr/resources.html#location-aware-resources  # noqa
    """

    __name__: Optional[str] = None
    __parent__: Optional["Resource"] = None

    def __init__(self, name: str, parent: "Resource") -> None:
        self.__name__ = name
        self.__parent__ = parent

    def add_child(self, child: "Resource") -> None:
        self[child.__name__] = child


class Root(Resource):
    def __init__(self, request: Request) -> None:
        self.add_child(LectureCollection(name="lectures", parent=self))


class LectureCollection(Resource):
    def models(self) -> List[LectureModel]:
        return LectureModel.all()

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

    def model(self) -> LectureModel:
        return LectureModel.get(self.chambre, self.session, self.num_texte, self.organe)


class AmendementCollection(Resource):
    def __getitem__(self, key: str) -> Resource:
        return AmendementResource(name=key, parent=self)


class AmendementResource(Resource):
    def __init__(self, name: str, parent: Resource) -> None:
        super().__init__(name=name, parent=parent)
        self.num = int(name)

    @property
    def lecture_resource(self) -> LectureResource:
        return self.__parent__.__parent__  # type: ignore

    def model(self) -> Optional[AmendementModel]:
        return (  # type: ignore
            DBSession.query(AmendementModel)
            .filter_by(
                chambre=self.lecture_resource.chambre,
                session=self.lecture_resource.session,
                num_texte=self.lecture_resource.num_texte,
                organe=self.lecture_resource.organe,
                num=self.num,
            )
            .first()
        )


class ArticleCollection(Resource):
    def __getitem__(self, key: str) -> Resource:
        try:
            subdiv_type, subdiv_num, subdiv_mult, subdiv_pos = key.split(".")
        except ValueError:
            raise KeyError
        return ArticleResource(
            name=key,
            parent=self,
            subdiv_type=subdiv_type,
            subdiv_num=subdiv_num,
            subdiv_mult=subdiv_mult,
            subdiv_pos=subdiv_pos,
        )


class ArticleResource(Resource):
    def __init__(
        self,
        name: str,
        parent: Resource,
        subdiv_type: str,
        subdiv_num: str,
        subdiv_mult: str,
        subdiv_pos: str,
    ) -> None:
        super().__init__(name=name, parent=parent)
        self.subdiv_type = subdiv_type
        self.subdiv_num = subdiv_num
        self.subdiv_mult = subdiv_mult
        self.subdiv_pos = subdiv_pos

    @property
    def lecture_resource(self) -> LectureResource:
        return self.__parent__.__parent__  # type: ignore
