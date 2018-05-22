from datetime import datetime

from .clean import clean_html
from .models import Amendement


def parse_amendement_from_csv(d_amend: dict) -> Amendement:
    return Amendement(  # type: ignore
        num=d_amend['Numéro '],
        article=d_amend['Subdivision '],
        alinea=d_amend['Alinéa'].strip(),
        auteur=d_amend['Auteur '],
        date_depot=parse_date(d_amend['Date de dépôt ']),
        sort=d_amend['Sort '],
        dispositif=clean_html(d_amend['Dispositif ']),
        objet=clean_html(d_amend['Objet ']),
    )


def parse_date(text):
    if text == '':
        return None
    return datetime.strptime(text, '%Y-%m-%d').date()


def parse_amendement_from_json(
    amend: dict,
    subdiv: dict,
) -> Amendement:
    return Amendement(  # type: ignore
        num=amend['num'],
        article=subdiv['libelle_subdivision'],
        alinea=amend['libelleAlinea'],
        auteur=amend['auteur'],
        sort=amend['sort'],
        identique=parse_bool(amend['isIdentique']),
        discussion_commune=(
            amend['idDiscussionCommune']
            if parse_bool(amend['isDiscussionCommune'])
            else None
        ),
    )


def parse_bool(text: str) -> bool:
    if text == 'true':
        return True
    if text == 'false':
        return False
    raise ValueError
