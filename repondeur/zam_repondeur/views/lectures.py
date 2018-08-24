import csv
import io
import logging
import transaction
from datetime import datetime
from typing import BinaryIO, Dict, TextIO, Tuple, Union

from pyramid.httpexceptions import HTTPBadRequest, HTTPFound, HTTPNotFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config, view_defaults

from zam_repondeur.fetch.an.dossiers.models import Chambre, Dossier, Lecture

from zam_repondeur.clean import clean_html
from zam_repondeur.data import get_data
from zam_repondeur.models import DBSession, Amendement, Lecture as LectureModel
from zam_repondeur.resources import (
    AmendementCollection,
    LectureCollection,
    LectureResource,
)
from zam_repondeur.tasks.fetch import fetch_articles, fetch_amendements
from zam_repondeur.utils import normalize_avis, normalize_num, normalize_reponse


class CSVError(Exception):
    pass


@view_config(context=LectureCollection, renderer="lectures_list.html")
def lectures_list(
    context: LectureCollection, request: Request
) -> Union[Response, dict]:
    lectures = context.models()
    if not lectures:
        return HTTPFound(request.resource_url(context, "add"))

    return {"lectures": lectures}


@view_defaults(context=LectureCollection, name="add")
class LecturesAdd:
    def __init__(self, context: LectureCollection, request: Request) -> None:
        self.context = context
        self.request = request
        self.dossiers_by_uid: Dict[str, Dossier] = get_data("dossiers")

    @view_config(request_method="GET", renderer="lectures_add.html")
    def get(self) -> dict:
        return {
            "dossiers": [
                {"uid": uid, "titre": dossier.titre}
                for uid, dossier in self.dossiers_by_uid.items()
            ]
        }

    @view_config(request_method="POST")
    def post(self) -> Response:
        dossier = self._get_dossier()
        lecture = self._get_lecture(dossier)

        chambre = lecture.chambre.value
        num_texte = lecture.texte.numero
        titre = lecture.titre
        organe = lecture.organe

        # FIXME: use date_depot to find the right session?
        if lecture.chambre == Chambre.AN:
            session = "15"
        else:
            session = "2017-2018"

        if LectureModel.exists(chambre, session, num_texte, organe):
            self.request.session.flash(("warning", "Cette lecture existe déjà..."))
        else:
            lecture = LectureModel.create(
                chambre, session, num_texte, titre, organe, dossier.titre
            )
            # Call to fetch_* tasks below being asynchronous, we need to make
            # sure the lecture already exists once and for all in the database
            # for future access. Otherwise, it may create many instances and
            # thus many objects within the database.
            transaction.commit()
            fetch_amendements(lecture, self.request.registry.settings)
            fetch_articles(lecture)
            self.request.session.flash(
                (
                    "success",
                    (
                        "Lecture créée avec succès, amendements et articles "
                        "en cours de récupération."
                    ),
                )
            )

        return HTTPFound(location=self.request.resource_url(self.context))

    def _get_dossier(self) -> Dossier:
        try:
            dossier_uid = self.request.POST["dossier"]
        except KeyError:
            raise HTTPBadRequest
        try:
            dossier = self.dossiers_by_uid[dossier_uid]
        except KeyError:
            raise HTTPNotFound
        return dossier

    def _get_lecture(self, dossier: Dossier) -> Lecture:
        try:
            texte, organe = self.request.POST["lecture"].split("-", 1)
        except (KeyError, ValueError):
            raise HTTPBadRequest
        matching = [
            lecture
            for lecture in dossier.lectures
            if lecture.texte.uid == texte and lecture.organe == organe
        ]
        if len(matching) != 1:
            raise HTTPNotFound
        return matching[0]


@view_defaults(context=LectureResource)
class LectureView:
    def __init__(self, context: LectureResource, request: Request) -> None:
        self.context = context
        self.request = request
        self.lecture = context.model()

    @view_config(request_method="POST")
    def post(self) -> Response:
        DBSession.delete(self.lecture)
        self.request.session.flash(("success", "Lecture supprimée avec succès."))
        return HTTPFound(location=self.request.resource_url(self.context.parent))


@view_defaults(context=AmendementCollection)
class ListAmendements:
    def __init__(self, context: AmendementCollection, request: Request) -> None:
        self.context = context
        self.request = request
        self.lecture = context.parent.model()
        self.amendements = self.lecture.amendements

    @view_config(request_method="GET", renderer="amendements.html")
    def get(self) -> dict:
        return {"lecture": self.lecture, "amendements": self.amendements}

    @view_config(request_method="POST")
    def post(self) -> Response:
        # We cannot just do `if not POST["reponses"]`, as FieldStorage does not want
        # to be cast to a boolean...
        if self.request.POST["reponses"] != b"":
            try:
                reponses_count, errors_count = self._import_reponses_from_csv_file(
                    reponses_file=self.request.POST["reponses"].file,
                    amendements={
                        amendement.num: amendement for amendement in self.amendements
                    },
                )
                if reponses_count:
                    self.request.session.flash(
                        ("success", f"{reponses_count} réponses chargées avec succès")
                    )
                    self.lecture.modified_at = datetime.utcnow()
                if errors_count:
                    self.request.session.flash(
                        (
                            "warning",
                            f"{errors_count} réponses n’ont pas pu être chargées. "
                            "Pour rappel, il faut que le fichier CSV contienne "
                            "au moins les noms de colonnes suivants "
                            "« Nº amdt », « Avis du Gouvernement », « Objet amdt » "
                            "et « Réponse ».",
                        )
                    )
            except CSVError as exc:
                self.request.session.flash(("danger", str(exc)))
        else:
            self.request.session.flash(
                ("warning", "Veuillez d’abord sélectionner un fichier")
            )

        return HTTPFound(location=self.request.resource_url(self.context))

    @staticmethod
    def _import_reponses_from_csv_file(
        reponses_file: BinaryIO, amendements: Dict[int, Amendement]
    ) -> Tuple[int, int]:
        previous_reponse = ""
        reponses_count = 0
        errors_count = 0

        reponses_text_file = io.TextIOWrapper(reponses_file, encoding="utf-8-sig")

        delimiter = ListAmendements._guess_csv_delimiter(reponses_text_file)

        for line in csv.DictReader(reponses_text_file, delimiter=delimiter):
            try:
                numero = line["Nº amdt"]
                avis = line["Avis du Gouvernement"] or ""
                objet = line["Objet amdt"] or ""
                reponse = line["Réponse"] or ""
            except KeyError:
                errors_count += 1
                continue

            try:
                num = normalize_num(numero)
            except ValueError:
                logging.warning("Invalid amendement number %r", num)
                errors_count += 1
                continue

            amendement = amendements.get(num)
            if not amendement:
                logging.warning("Could not find amendement number %r", num)
                errors_count += 1
                continue

            amendement.avis = normalize_avis(avis)
            amendement.observations = clean_html(objet)
            reponse = normalize_reponse(reponse, previous_reponse)
            amendement.reponse = clean_html(reponse)
            if "Commentaires" in line:
                amendement.comments = clean_html(line["Commentaires"])
            previous_reponse = reponse
            reponses_count += 1

        return reponses_count, errors_count

    @staticmethod
    def _guess_csv_delimiter(text_file: TextIO) -> str:
        try:
            sample = text_file.readline()
        except UnicodeDecodeError:
            raise CSVError("Le fichier n’est pas encodé en UTF-8")
        except Exception:
            raise CSVError("Le format du fichier n’est pas reconnu")

        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
        except csv.Error:
            raise CSVError(
                "Le fichier CSV n’utilise pas un délimiteur reconnu "
                "(virgule, point-virgule ou tabulation)"
            )

        text_file.seek(0)

        return dialect.delimiter


@view_config(context=LectureResource, name="manual_refresh")
def manual_refresh(context: LectureResource, request: Request) -> Response:
    lecture = context.model()
    fetch_amendements(lecture, request.registry.settings)
    fetch_articles(lecture)
    return HTTPFound(location=request.resource_url(context, "journal"))


@view_config(context=LectureResource, name="check", renderer="json")
def lecture_check(context: LectureResource, request: Request) -> dict:
    lecture = context.model()
    return {"modified_at": lecture.modified_at_timestamp}


@view_config(route_name="choices_lectures", renderer="json")
def choices_lectures(request: Request) -> dict:
    uid = request.matchdict["uid"]
    dossiers_by_uid = get_data("dossiers")
    dossier = dossiers_by_uid[uid]
    return {
        "lectures": [
            {
                "key": f"{lecture.texte.uid}-{lecture.organe}",
                "label": " – ".join(
                    [
                        str(lecture.chambre),
                        lecture.titre,
                        f"Texte Nº {lecture.texte.numero}",
                    ]
                ),
            }
            for lecture in dossier.lectures
        ]
    }
