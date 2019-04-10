import logging
from collections import Counter
from typing import Dict

from pyramid.request import Request

from zam_repondeur.clean import clean_html
from zam_repondeur.models import Amendement, Lecture, User, get_one_or_create
from zam_repondeur.models.events.amendement import (
    AmendementTransfere,
    AvisAmendementModifie,
    ObjetAmendementModifie,
    ReponseAmendementModifiee,
    CommentsAmendementModifie,
)
from zam_repondeur.utils import normalize_avis, normalize_num, normalize_reponse


def import_amendement(
    request: Request,
    lecture: Lecture,
    amendements: Dict[int, Amendement],
    item: dict,
    counter: Counter,
    previous_reponse: str,
) -> None:
    try:
        numero = item["num"]
        avis = item["avis"] or ""
        objet = item["objet"] or ""
        reponse = item["reponse"] or ""
    except KeyError:
        counter["reponses_errors"] += 1
        return

    try:
        num = normalize_num(numero)
    except ValueError:
        logging.warning("Invalid amendement number %r", numero)
        counter["reponses_errors"] += 1
        return

    amendement = amendements.get(num)
    if not amendement:
        logging.warning("Could not find amendement number %r", num)
        counter["reponses_errors"] += 1
        return

    avis = normalize_avis(avis)
    if avis != (amendement.user_content.avis or ""):
        AvisAmendementModifie.create(request, amendement, avis)

    objet = clean_html(objet)
    if objet != (amendement.user_content.objet or ""):
        ObjetAmendementModifie.create(request, amendement, objet)

    reponse = clean_html(normalize_reponse(reponse, previous_reponse))
    if reponse != (amendement.user_content.reponse or ""):
        ReponseAmendementModifiee.create(request, amendement, reponse)

    if "comments" in item:
        comments = clean_html(item["comments"])
        if comments != (amendement.user_content.comments or ""):
            CommentsAmendementModifie.create(request, amendement, comments)

    if "affectation_email" in item and item["affectation_email"]:
        transfer_amendement(request, lecture, amendement, item)

    previous_reponse = reponse
    counter["reponses"] += 1


def transfer_amendement(
    request: Request, lecture: Lecture, amendement: Amendement, item: dict
) -> None:
    email = User.normalize_email(item["affectation_email"])

    if not User.validate_email(email):
        logging.warning("Invalid email address %r", email)
        return

    user, created = get_one_or_create(User, email=email)
    if created:
        affectation_name = User.normalize_name(item["affectation_name"])
        user.name = affectation_name if affectation_name != "" else email
        if lecture.owned_by_team:
            user.teams.append(lecture.owned_by_team)

    target_table = user.table_for(lecture)
    old = str(amendement.user_table.user) if amendement.user_table else ""
    new = str(target_table.user) if target_table else ""
    if amendement.user_table is target_table:
        return
    amendement.user_table = target_table
    AmendementTransfere.create(request, amendement, old, new)
