import csv
import io
import logging
import transaction
from datetime import datetime
from typing import BinaryIO, Dict, Optional, TextIO, Tuple, Union

import ujson as json
from pyramid.httpexceptions import HTTPBadRequest, HTTPFound, HTTPNotFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config, view_defaults
from sqlalchemy.orm import joinedload

from zam_repondeur.clean import clean_html
from zam_repondeur.data import get_data
from zam_repondeur.fetch.an.dossiers.models import Dossier, Lecture
from zam_repondeur.message import Message
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
        lectures = self.context.models()
        return {
            "dossiers": [
                {"uid": uid, "titre": dossier.titre}
                for uid, dossier in self.dossiers_by_uid.items()
            ],
            "lectures": lectures,
        }

    @view_config(request_method="POST")
    def post(self) -> Response:
        dossier = self._get_dossier()
        lecture = self._get_lecture(dossier)

        chambre = lecture.chambre.value
        num_texte = lecture.texte.numero
        titre = lecture.titre
        organe = lecture.organe
        partie = lecture.partie

        session = lecture.get_session()

        if LectureModel.exists(chambre, session, num_texte, partie, organe):
            self.request.session.flash(
                Message(cls="warning", text="Cette lecture existe déjà...")
            )
            return HTTPFound(location=self.request.resource_url(self.context))

        lecture_model: LectureModel = LectureModel.create(
            chambre=chambre,
            session=session,
            num_texte=num_texte,
            partie=partie,
            titre=titre,
            organe=organe,
            dossier_legislatif=dossier.titre,
        )
        # Call to fetch_* tasks below being asynchronous, we need to make
        # sure the lecture_model already exists once and for all in the database
        # for future access. Otherwise, it may create many instances and
        # thus many objects within the database.
        transaction.commit()
        fetch_amendements(lecture_model.pk)
        fetch_articles(lecture_model.pk)
        self.request.session.flash(
            Message(
                cls="success",
                text=(
                    "Lecture créée avec succès, amendements et articles "
                    "en cours de récupération."
                ),
            )
        )
        return HTTPFound(
            location=self.request.resource_url(
                self.context[lecture_model.url_key], "amendements"
            )
        )

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
            texte, organe, partie_str = self.request.POST["lecture"].split("-", 2)
        except (KeyError, ValueError):
            raise HTTPBadRequest
        partie: Optional[int]
        if partie_str == "":
            partie = None
        else:
            partie = int(partie_str)
        matching = [
            lecture
            for lecture in dossier.lectures
            if (
                lecture.texte.uid == texte
                and lecture.organe == organe
                and lecture.partie == partie
            )
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
        DBSession.flush()
        self.request.session.flash(
            Message(cls="success", text="Lecture supprimée avec succès.")
        )
        return HTTPFound(location=self.request.resource_url(self.context.parent))


@view_defaults(context=AmendementCollection)
class ListAmendements:
    def __init__(self, context: AmendementCollection, request: Request) -> None:
        self.context = context
        self.request = request
        self.lecture = context.parent.model(joinedload("articles"))
        self.amendements = self.lecture.amendements

    @view_config(request_method="GET", renderer="amendements.html")
    def get(self) -> dict:
        check_url = self.request.resource_path(self.context.parent, "check")
        return {
            "lecture": self.lecture,
            "amendements": self.amendements,
            "check_url": check_url,
            "timestamp": self.lecture.modified_at_timestamp,
        }

    @view_config(request_method="POST")
    def post(self) -> Response:
        if "reponses" in self.request.POST:
            # We cannot just do `if not POST["reponses"]`, as FieldStorage does not want
            # to be cast to a boolean...
            if self.request.POST["reponses"] != b"":
                try:
                    reponses_count, errors_count = self._import_reponses_from_csv_file(
                        reponses_file=self.request.POST["reponses"].file,
                        amendements={
                            amendement.num: amendement
                            for amendement in self.amendements
                        },
                    )
                    if reponses_count:
                        self.request.session.flash(
                            Message(
                                cls="success",
                                text=f"{reponses_count} réponses chargées avec succès",
                            )
                        )
                        self.lecture.modified_at = datetime.utcnow()
                    if errors_count:
                        self.request.session.flash(
                            Message(
                                cls="warning",
                                text=(
                                    f"{errors_count} réponses n’ont pas pu être "
                                    "chargées. Pour rappel, il faut que le fichier CSV "
                                    "contienne au moins les noms de colonnes suivants "
                                    "« Num amdt », « Avis du Gouvernement », "
                                    "« Objet amdt » et « Réponse »."
                                ),
                            )
                        )
                except CSVError as exc:
                    self.request.session.flash(Message(cls="danger", text=str(exc)))
            else:
                self.request.session.flash(
                    Message(
                        cls="warning", text="Veuillez d’abord sélectionner un fichier"
                    )
                )
        if "backup" in self.request.POST:
            # We cannot just do `if not POST["backup"]`, as FieldStorage does not want
            # to be cast to a boolean...
            if self.request.POST["backup"] != b"":
                try:
                    reponses_count, errors_count = self._import_backup_from_json_file(
                        backup_file=self.request.POST["backup"].file,
                        amendements={
                            amendement.num: amendement
                            for amendement in self.amendements
                        },
                    )
                    if reponses_count:
                        self.request.session.flash(
                            Message(
                                cls="success",
                                text=f"{reponses_count} réponses chargées avec succès",
                            )
                        )
                        self.lecture.modified_at = datetime.utcnow()
                    if errors_count:
                        self.request.session.flash(
                            Message(
                                cls="warning",
                                text=(
                                    "Le fichier de sauvegarde n’a pas pu être chargé "
                                    f"pour {errors_count} amendement(s)."
                                ),
                            )
                        )
                except CSVError as exc:
                    self.request.session.flash(Message(cls="danger", text=str(exc)))
            else:
                self.request.session.flash(
                    Message(
                        cls="warning", text="Veuillez d’abord sélectionner un fichier"
                    )
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
                numero = line["Num amdt"]
                avis = line["Avis du Gouvernement"] or ""
                objet = line["Objet amdt"] or ""
                reponse = line["Réponse"] or ""
            except KeyError:
                errors_count += 1
                continue

            try:
                num = normalize_num(numero)
            except ValueError:
                logging.warning("Invalid amendement number %r", numero)
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
            if "Affectation" in line:
                amendement.affectation = clean_html(line["Affectation"])
            if "Commentaires" in line:
                amendement.comments = clean_html(line["Commentaires"])
            previous_reponse = reponse
            reponses_count += 1

        return reponses_count, errors_count

    @staticmethod
    def _import_backup_from_json_file(
        backup_file: BinaryIO, amendements: Dict[int, Amendement]
    ) -> Tuple[int, int]:
        previous_reponse = ""
        reponses_count = 0
        errors_count = 0

        for line in json.loads(backup_file.read().decode("utf-8-sig"))["amendements"]:
            try:
                numero = line["num"]
                avis = line["avis"] or ""
                objet = line["observations"] or ""
                reponse = line["reponse"] or ""
            except KeyError:
                errors_count += 1
                continue

            try:
                num = normalize_num(numero)
            except ValueError:
                logging.warning("Invalid amendement number %r", numero)
                errors_count += 1
                continue

            amendement = amendements.get(num)
            if not amendement:
                logging.warning("Could not find amendement number %r", num)
                errors_count += 1
                continue

            amendement.avis = normalize_avis(avis)
            amendement.observations = objet
            reponse = normalize_reponse(reponse, previous_reponse)
            amendement.reponse = reponse
            if "affectation" in line:
                amendement.affectation = line["affectation"]
            if "comments" in line:
                amendement.comments = line["comments"]
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
    fetch_amendements(lecture.pk)
    fetch_articles(lecture.pk)
    request.session.flash(
        Message(
            cls="success",
            text=(
                "Rafraichissement des amendements et des articles en cours. "
                "Vous serez notifié·e dès que les nouvelles informations "
                "seront disponibles."
            ),
        )
    )
    return HTTPFound(location=request.resource_url(context, "amendements"))


@view_config(context=LectureResource, name="check", renderer="json")
def lecture_check(context: LectureResource, request: Request) -> dict:
    lecture = context.model()
    timestamp = float(request.GET["since"])
    modified_at = lecture.modified_at_timestamp
    modified_amendements_numbers: list = []
    if timestamp < modified_at:
        modified_amendements_numbers = lecture.modified_amendements_numbers_since(
            timestamp
        )
    return {
        "modified_amendements_numbers": modified_amendements_numbers,
        "modified_at": modified_at,
    }


@view_config(route_name="choices_lectures", renderer="json")
def choices_lectures(request: Request) -> dict:
    uid = request.matchdict["uid"]
    dossiers_by_uid = get_data("dossiers")
    dossier = dossiers_by_uid[uid]
    return {
        "lectures": [
            {"key": lecture.key, "label": lecture.label} for lecture in dossier.lectures
        ]
    }
