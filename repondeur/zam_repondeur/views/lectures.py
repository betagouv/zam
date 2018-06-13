from pyramid.httpexceptions import HTTPBadRequest, HTTPFound, HTTPNotFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config, view_defaults
from sqlalchemy.sql.expression import case

from zam_repondeur.fetch import get_amendements_senat, NotFound
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
        return self._form_data()

    @view_config(request_method="POST")
    def post(self) -> Response:
        chambre = self.request.POST["chambre"]
        session = self.request.POST["session"]
        num_texte = self.request.POST["num_texte"]
        if chambre not in CHAMBRES:
            raise HTTPBadRequest

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

    def _form_data(self) -> dict:
        return {
            "chambres": CHAMBRES.items(),
            "sessions": [(sess, sess) for sess in SESSIONS],
        }


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

    if chambre != "senat":
        return HTTPBadRequest(f'Invalid value "{chambre}" for "chambre" param')

    try:
        amendements = get_amendements_senat(session, num_texte)
    except NotFound:
        request.session.flash(("danger", "Aucun amendement n'a pu être trouvé."))

    if amendements:
        DBSession.add_all(amendements)
        DBSession.flush()
        request.session.flash(("success", f"{len(amendements)} amendements"))

    return HTTPFound(
        location=request.route_url(
            "lecture", chambre=chambre, session=session, num_texte=num_texte
        )
    )
