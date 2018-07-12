from typing import List, Optional

from pyramid.request import Request

from zam_repondeur.models import Lecture as LectureModel


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

    def model(self) -> LectureModel:
        return LectureModel.get(self.chambre, self.session, self.num_texte, self.organe)
