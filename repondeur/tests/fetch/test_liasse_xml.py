from datetime import date
from pathlib import Path


SAMPLE_LIASSE = Path(__file__).parent.parent / "sample_data" / "liasse.xml"


def test_import_liasse_xml(article1_an):
    from zam_repondeur.fetch.an.liasse_xml import import_liasse_xml
    from zam_repondeur.models import Amendement

    amendements = import_liasse_xml(SAMPLE_LIASSE.open(mode="rb"))

    assert isinstance(amendements, list)
    assert len(amendements) == 3
    assert all(isinstance(item, Amendement) for item in amendements)

    _check_amendement_0(amendements[0])
    _check_amendement_1(amendements[1])
    _check_amendement_gouvernemental(amendements[2])


def _check_amendement_0(amendement):

    assert amendement.lecture.chambre == "an"
    assert amendement.lecture.session == "15"
    assert amendement.lecture.num_texte == 806
    assert amendement.lecture.organe == "PO744107"

    assert amendement.article.type == "article"
    assert amendement.article.num == "2"
    assert amendement.article.mult == ""
    assert amendement.article.pos == ""
    assert amendement.article.titre is None
    assert amendement.article.contenu is None

    assert amendement.alinea == 24

    assert amendement.num == 28
    assert amendement.rectif == 0

    assert amendement.auteur == "Fabrice Brun"
    assert amendement.matricule == "PA718838"
    assert amendement.groupe == "Les Républicains"

    assert amendement.date_depot == date(2018, 6, 7)

    assert amendement.sort == ""

    assert amendement.position is None  # no order yet
    assert amendement.discussion_commune is None
    assert amendement.identique is None

    assert amendement.parent is None

    assert (
        amendement.dispositif
        == "<div>Cet amendement est en cours de traitement par les services de l'Assemblée.</div>"  # noqa
    )
    assert amendement.objet == ""

    assert amendement.resume is None

    assert amendement.avis is None
    assert amendement.observations is None
    assert amendement.reponse is None

    assert amendement.bookmarked_at is None


def _check_amendement_1(amendement):

    assert amendement.lecture.chambre == "an"
    assert amendement.lecture.session == "15"
    assert amendement.lecture.num_texte == 806
    assert amendement.lecture.organe == "PO744107"

    assert amendement.article.type == "annexe"
    assert amendement.article.num == ""
    assert amendement.article.mult == ""
    assert amendement.article.pos == ""
    assert amendement.article.titre is None
    assert amendement.article.contenu is None

    assert amendement.alinea == 12

    assert amendement.num == 26
    assert amendement.rectif == 0

    assert amendement.auteur == "Fabrice Brun"
    assert amendement.matricule == "PA718838"
    assert amendement.groupe == "Les Républicains"

    assert amendement.date_depot == date(2018, 6, 7)

    assert amendement.sort == "Retiré"

    assert amendement.position is None  # no order yet
    assert amendement.discussion_commune is None
    assert amendement.identique is None

    assert amendement.parent.num == 28
    assert amendement.parent.rectif == 0

    assert amendement.dispositif == (
        "<p>L’alinéa 12 est complété par l’alinéa suivant :</p>\n"
        "<p>« L’article préliminaire du projet de loi pour un état "
        "au service d’une société de confiance définit les objectifs "
        "de l’action publique à horizon 2022. Elle s’articule autour "
        "de l’affirmation de principes généraux d’organisation et d’action, "
        "lesquels nécessitent des compléments. »</p>"
    )
    assert amendement.objet == (
        "<p>L’article préliminaire du projet de loi pour un état au service "
        "d’une société de confiance définit les objectifs de l’action publique "
        "à horizon 2022. Elle s’articule autour de l’affirmation de principes "
        "généraux d’organisation et d’action, lesquels nécessitent des "
        "compléments, c’est l’objet du présent amendement qui prévoit que les "
        "statistiques sur la mise en œuvre des pénalités devront être publiées, "
        "en distinguant celles qui figurent dans les propositions de "
        "rectification ou les notifications de bases imposées d’office et "
        "celles qui sont maintenues à l’issue de la procédure de redressement</p>"
    )

    assert amendement.resume is None

    assert amendement.avis is None
    assert amendement.observations is None
    assert amendement.reponse is None

    assert amendement.bookmarked_at is None


def _check_amendement_gouvernemental(amendement):
    assert amendement.auteur == "LE GOUVERNEMENT"
    assert amendement.matricule is None
    assert amendement.groupe is None
    assert amendement.gouvernemental
