import logging
from collections import Counter
from typing import Dict

from pyramid.request import Request

from zam_repondeur.models import (
    Amendement,
    Lecture,
    SharedTable,
    Team,
    User,
    UserTable,
    get_one_or_create,
)
from zam_repondeur.models.events.amendement import (
    AmendementTransfere,
    AvisAmendementModifie,
    CommentsAmendementModifie,
    ObjetAmendementModifie,
    ReponseAmendementModifiee,
)
from zam_repondeur.services.clean import clean_html
from zam_repondeur.utils import normalize_avis, normalize_num, normalize_reponse

logger = logging.getLogger(__name__)


def import_amendement(
    request: Request,
    lecture: Lecture,
    amendements: Dict[str, Amendement],
    item: dict,
    counter: Counter,
    previous_reponse: str,
    team: Team,
) -> None:
    try:
        numero = item["num"]
        avis = item["avis"] or ""
        objet = item["objet"] or ""
        reponse = item["reponse"] or ""
    except KeyError:
        counter["reponses_errors"] += 1
        return

    num = normalize_num(str(numero))

    amendement = amendements.get(num)
    if not amendement:
        logging.warning("Could not find amendement number %r", num)
        counter["reponses_errors"] += 1
        return

    avis = normalize_avis(avis)
    if avis != (amendement.user_content.avis or ""):
        AvisAmendementModifie.create(amendement=amendement, avis=avis, request=request)

    objet = clean_html(objet)
    if objet != (amendement.user_content.objet or ""):
        ObjetAmendementModifie.create(
            amendement=amendement, objet=objet, request=request
        )

    reponse = clean_html(normalize_reponse(reponse, previous_reponse))
    if reponse != (amendement.user_content.reponse or ""):
        ReponseAmendementModifiee.create(
            amendement=amendement, reponse=reponse, request=request
        )

    if "comments" in item:
        comments = clean_html(item["comments"])
        if comments != (amendement.user_content.comments or ""):
            CommentsAmendementModifie.create(
                amendement=amendement, comments=comments, request=request
            )

    # Order matters, if there is a box *and* an email, the amendement will be
    # transfered to the box then to the user who has precedence.
    if "affectation_box" in item and item["affectation_box"]:
        _transfer_to_box_amendement_on_import(request, lecture, amendement, item)

    if "affectation_email" in item and item["affectation_email"]:
        _transfer_to_user_amendement_on_import(request, lecture, amendement, item, team)

    previous_reponse = reponse
    counter["reponses"] += 1


def _transfer_to_box_amendement_on_import(
    request: Request, lecture: Lecture, amendement: Amendement, item: dict
) -> None:
    shared_table, created = get_one_or_create(
        SharedTable, titre=item["affectation_box"], lecture=lecture
    )

    if amendement.location.shared_table is shared_table:
        return

    old = amendement.table_name_with_email
    new = shared_table.titre

    amendement.location.shared_table = shared_table
    amendement.location.user_table = None

    AmendementTransfere.create(
        amendement=amendement, old_value=old, new_value=new, request=request
    )


def _transfer_to_user_amendement_on_import(
    request: Request, lecture: Lecture, amendement: Amendement, item: dict, team: Team
) -> None:
    email = User.normalize_email(item["affectation_email"])

    if not User.email_is_well_formed(email):
        logger.warning("Invalid email address %r", email)
        return

    user, created = get_one_or_create(User, email=email)
    if created:
        affectation_name = User.normalize_name(item["affectation_name"])
        user.name = affectation_name if affectation_name != "" else email
        user.teams.append(team)

    user_table, _ = get_one_or_create(UserTable, user=user, lecture=lecture)
    if amendement.location.user_table is user_table:
        return

    old = amendement.table_name_with_email
    new = str(user)

    amendement.location.user_table = user_table
    amendement.location.shared_table = None

    AmendementTransfere.create(
        amendement=amendement, old_value=old, new_value=new, request=request
    )
