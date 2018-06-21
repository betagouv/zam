import csv
import io
from typing import BinaryIO, Dict

from pyramid.httpexceptions import HTTPBadRequest, HTTPFound, HTTPNotFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config, view_defaults
from sqlalchemy.sql.expression import case

from zam_aspirateur.textes.dossiers_legislatifs import get_dossiers_legislatifs
from zam_aspirateur.textes.models import Chambre

from zam_repondeur.fetch import get_amendements
from zam_repondeur.models import DBSession, Amendement, Lecture, CHAMBRES
from zam_repondeur.utils import normalize_avis, normalize_num, normalize_reponse


CURRENT_LEGISLATURE = 15


@view_config(route_name="lectures_list", renderer="lectures_list.html")
def lectures_list(request: Request) -> dict:
    return {"lectures": Lecture.all()}


@view_defaults(route_name="lectures_add", renderer="lectures_add.html")
class LecturesAdd:
    def __init__(self, request: Request) -> None:
        self.request = request
        self.dossiers_by_uid = get_dossiers_legislatifs(legislature=CURRENT_LEGISLATURE)
        self.lectures_by_dossier = {
            dossier.uid: {
                lecture.texte.uid: f"{lecture.chambre} – {lecture.titre} (texte nº {lecture.texte.numero} déposé le {lecture.texte.date_depot.strftime('%d/%m/%Y')})"  # noqa
                for lecture in dossier.lectures.values()
            }
            for dossier in self.dossiers_by_uid.values()
        }

    @view_config(request_method="GET")
    def get(self) -> dict:
        return {
            "dossiers": list(self.dossiers_by_uid.values()),
            "lectures_by_dossier": self.lectures_by_dossier,
        }

    @view_config(request_method="POST")
    def post(self) -> Response:
        dossier_uid = self.request.POST["dossier"]
        texte_uid = self.request.POST["lecture"]

        dossier = self.dossiers_by_uid[dossier_uid]
        lecture = dossier.lectures[texte_uid]

        chambre = lecture.chambre.value
        num_texte = lecture.texte.numero

        # FIXME: use date_depot to find the right session?
        if lecture.chambre == Chambre.AN:
            session = "15"
        else:
            session = "2017-2018"

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
def lecture(request: Request) -> dict:
    lecture = Lecture.get(
        chambre=request.matchdict["chambre"],
        session=request.matchdict["session"],
        num_texte=int(request.matchdict["num_texte"]),
    )
    if lecture is None:
        raise HTTPNotFound

    amendements_count = (
        DBSession.query(Amendement)
        .filter(
            Amendement.chambre == lecture.chambre,
            Amendement.session == lecture.session,
            Amendement.num_texte == lecture.num_texte,
        )
        .count()
    )
    return {"lecture": lecture, "amendements_count": amendements_count}


@view_defaults(route_name="list_amendements")
class ListAmendements:
    def __init__(self, request: Request) -> None:
        self.request = request
        self.lecture = Lecture.get(
            chambre=request.matchdict["chambre"],
            session=request.matchdict["session"],
            num_texte=int(request.matchdict["num_texte"]),
        )
        if self.lecture is None:
            raise HTTPNotFound

        self.amendements = (
            DBSession.query(Amendement)
            .filter(
                Amendement.chambre == self.lecture.chambre,
                Amendement.session == self.lecture.session,
                Amendement.num_texte == self.lecture.num_texte,
            )
            .order_by(
                case([(Amendement.position.is_(None), 1)], else_=0),
                Amendement.position,
                Amendement.num,
            )
            .all()
        )

    @view_config(request_method="GET", renderer="amendements.html")
    def get(self) -> dict:
        return {"lecture": self.lecture, "amendements": self.amendements}

    @view_config(request_method="POST")
    def post(self) -> Response:
        reponses_file = self.request.POST["reponses"].file

        amendements_by_num = {
            amendement.num: amendement for amendement in self.amendements
        }

        reponses_count = self._import_reponses_from_csv_file(
            reponses_file, self.lecture, amendements_by_num
        )

        self.request.session.flash(("success", f"{reponses_count} réponses chargées"))

        return HTTPFound(
            location=self.request.route_url(
                "list_amendements",
                chambre=self.lecture.chambre,
                session=self.lecture.session,
                num_texte=self.lecture.num_texte,
            )
        )

    @staticmethod
    def _import_reponses_from_csv_file(
        reponses_file: BinaryIO, lecture: Lecture, amendements: Dict[int, Amendement]
    ) -> int:
        previous_reponse = ""
        reponses_count = 0
        for i, line in enumerate(csv.DictReader(io.TextIOWrapper(reponses_file))):
            num = normalize_num(line["N°"])
            amendement = amendements.get(num)
            if amendement:
                amendement.position = i
                amendement.avis = normalize_avis(line["Avis du Gouvernement"])
                amendement.observations = line["Objet (article / amdt)"]
                reponse = normalize_reponse(
                    line["Avis et observations de l'administration référente"],
                    previous_reponse,
                    lecture,
                )
                amendement.reponse = reponse
                previous_reponse = reponse
                reponses_count += 1
        return reponses_count


@view_config(route_name="fetch_amendements")
def fetch_amendements(request: Request) -> Response:
    chambre = request.matchdict["chambre"]
    session = request.matchdict["session"]
    num_texte = int(request.matchdict["num_texte"])

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
