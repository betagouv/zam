from pyramid.httpexceptions import HTTPBadRequest, HTTPFound, HTTPNotFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config, view_defaults
from sqlalchemy.sql.expression import case

from zam_repondeur.fetch import get_amendements
from zam_repondeur.models import DBSession, Amendement, Lecture, CHAMBRES, SESSIONS


@view_config(route_name="lectures_list", renderer="lectures_list.html")
def lectures_list(request: Request) -> dict:
    return {"lectures": Lecture.all()}


@view_defaults(route_name="lectures_add", renderer="lectures_add.html")
class LecturesAdd:
    def __init__(self, request: Request) -> None:
        self.request = request

    @view_config(request_method="GET")
    def get(self) -> dict:
        return {"chambres": CHAMBRES, "sessions": SESSIONS}

    @view_config(request_method="POST")
    def post(self) -> Response:
        chambre = self.request.POST["chambre"]
        session = self.request.POST["session"]
        num_texte = self.request.POST["num_texte"]
        if chambre not in CHAMBRES:
            raise HTTPBadRequest

        if chambre == "an":
            num_texte = f"{int(num_texte):04}"

        if Lecture.exists(chambre, session, num_texte):
            self.request.session.flash(("warning", "Cette lecture existe déjà..."))
        else:
            Lecture.create(chambre, session, num_texte)
            self.request.session.flash(("success", "Lecture créée avec succès."))

        return HTTPFound(
            location=self.request.route_url(
                "lecture", chambre=chambre, session=session, num_texte=num_texte
            )
        )


@view_config(route_name="lecture", renderer="lecture.html")
@view_config(route_name="list_amendements", renderer="amendements.html")
def lecture(request: Request) -> dict:
    lecture = Lecture.get(
        chambre=request.matchdict["chambre"],
        session=request.matchdict["session"],
        num_texte=request.matchdict["num_texte"],
    )
    if lecture is None:
        raise HTTPNotFound

    amendements = (
        DBSession.query(Amendement)
        .filter(
            Amendement.chambre == lecture.chambre,
            Amendement.session == lecture.session,
            Amendement.num_texte == lecture.num_texte,
        )
        .order_by(
            case([(Amendement.position.is_(None), 1)], else_=0),
            Amendement.position,
            Amendement.num,
        )
        .all()
    )
    return {"lecture": lecture, "amendements": amendements}


@view_config(route_name="fetch_amendements")
def fetch_amendements(request: Request) -> Response:
    chambre = request.matchdict["chambre"]
    session = request.matchdict["session"]
    num_texte = request.matchdict["num_texte"]

    if chambre not in CHAMBRES:
        return HTTPBadRequest(f'Invalid value "{chambre}" for "chambre" param')

    amendements = get_amendements(chambre, session, num_texte)

    if amendements:
        DBSession.add_all(amendements)
        DBSession.flush()
        request.session.flash(("success", f"{len(amendements)} amendements"))
    else:
        request.session.flash(("danger", "Aucun amendement n'a pu être trouvé."))

    return HTTPFound(
        location=request.route_url(
            "lecture", chambre=chambre, session=session, num_texte=num_texte
        )
    )
