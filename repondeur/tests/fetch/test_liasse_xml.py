from datetime import date
from pathlib import Path


SAMPLE_LIASSE = Path(__file__).parent.parent / "sample_data" / "liasse.xml"


def test_import_liasse_xml():
    from zam_repondeur.fetch.an.liasse_xml import import_liasse_xml
    from zam_repondeur.fetch.models import Amendement

    amendements = import_liasse_xml(SAMPLE_LIASSE.open(mode="rb"))

    assert isinstance(amendements, list)
    assert len(amendements) == 2
    assert all(isinstance(item, Amendement) for item in amendements)

    _check_amendement_0(amendements[0])
    _check_amendement_1(amendements[1])


def _check_amendement_0(amendement):

    assert amendement.chambre == "an"
    assert amendement.session == "15"  # legislature

    assert amendement.num_texte == 806
    assert amendement.organe == "PO744107"

    assert amendement.subdiv_type == "article"
    assert amendement.subdiv_num == "2"
    assert amendement.subdiv_mult == ""
    assert amendement.subdiv_pos == ""
    assert amendement.subdiv_titre == ""
    assert amendement.subdiv_contenu == ""

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

    assert amendement.parent_num is None
    assert amendement.parent_rectif is None

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

    assert amendement.chambre == "an"
    assert amendement.session == "15"  # legislature

    assert amendement.num_texte == 806
    assert amendement.organe == "PO744107"

    assert amendement.subdiv_type == "annexe"
    assert amendement.subdiv_num == ""
    assert amendement.subdiv_mult == ""
    assert amendement.subdiv_pos == ""
    assert amendement.subdiv_titre == ""
    assert amendement.subdiv_contenu == ""

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

    assert amendement.parent_num == 28
    assert amendement.parent_rectif == 0

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
