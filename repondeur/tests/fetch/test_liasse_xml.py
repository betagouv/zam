from datetime import date
from pathlib import Path

import pytest
import transaction


def open_liasse(filename):
    return (Path(__file__).parent.parent / "sample_data" / filename).open(mode="rb")


def test_import_liasse_xml(lecture_essoc):
    from zam_repondeur.fetch.an.liasse_xml import import_liasse_xml
    from zam_repondeur.models import Amendement

    amendements, errors = import_liasse_xml(open_liasse("liasse.xml"), lecture_essoc)

    assert isinstance(amendements, list)
    assert len(amendements) == 3
    assert all(isinstance(item, Amendement) for item in amendements)

    _check_amendement_0(amendements[0])
    _check_amendement_1(amendements[1])
    _check_amendement_gouvernemental(amendements[2])

    assert errors == []


def test_import_liasse_xml_article_additionnel(lecture_essoc):
    from zam_repondeur.fetch.an.liasse_xml import import_liasse_xml

    amendements, errors = import_liasse_xml(
        open_liasse("liasse_apres.xml"), lecture_essoc
    )

    assert amendements[0].article.num == "2"
    assert amendements[0].article.pos == "après"

    assert errors == []


def test_import_same_liasse_xml_again_preserve_response(lecture_essoc):
    from zam_repondeur.fetch.an.liasse_xml import import_liasse_xml

    # Let's import amendements
    amendements, _ = import_liasse_xml(open_liasse("liasse.xml"), lecture_essoc)

    # Now let's add a response
    amendements[1].user_content.avis = "Favorable"
    amendements[1].user_content.objet = "Objet"
    amendements[1].user_content.reponse = "Réponse"

    # And import the same amendements again
    amendements2, errors = import_liasse_xml(open_liasse("liasse.xml"), lecture_essoc)

    assert amendements == amendements2
    assert amendements2[1].user_content.avis == "Favorable"
    assert amendements2[1].user_content.objet == "Objet"
    assert amendements2[1].user_content.reponse == "Réponse"

    assert errors == []


def test_import_smaller_liasse_xml_preserves_responses(lecture_essoc):
    from zam_repondeur.fetch.an.liasse_xml import import_liasse_xml
    from zam_repondeur.models import Amendement, DBSession

    # Let's import amendements
    amendements, _ = import_liasse_xml(open_liasse("liasse.xml"), lecture_essoc)

    # Now let's add a response
    amendements[1].user_content.avis = "Favorable"
    amendements[1].user_content.objet = "Objet"
    amendements[1].user_content.reponse = "Réponse"

    # Even for the one not being reimported
    amendements[2].user_content.avis = "Défavorable"
    amendements[2].user_content.objet = "Objet"
    amendements[2].user_content.reponse = "Réponse"

    # And import a smaller liasse
    amendements2, errors = import_liasse_xml(
        open_liasse("liasse_smaller.xml"), lecture_essoc
    )

    assert amendements[0] == amendements2[0]
    assert amendements[1] == amendements2[1]
    assert len(amendements2) == 2
    assert amendements2[1].user_content.avis == "Favorable"
    assert amendements2[1].user_content.objet == "Objet"
    assert amendements2[1].user_content.reponse == "Réponse"
    assert DBSession.query(Amendement).count() == 3
    assert amendements[2].user_content.avis == "Défavorable"

    assert errors == []


def test_import_liasse_xml_with_unknown_parent(lecture_essoc):
    from zam_repondeur.fetch.an.liasse_xml import import_liasse_xml

    # Let's import a liasse with only a child amendement
    amendements, errors = import_liasse_xml(
        open_liasse("liasse_only_child.xml"), lecture_essoc
    )

    assert amendements == []
    assert len(errors) == 1
    uid, cause = errors[0]
    assert uid == "AMANR5L15PO744107B0806P0D1N26"
    assert cause == "Unknown parent amendement 28"


def test_import_liasse_xml_with_known_but_missing_parent(lecture_essoc):
    from zam_repondeur.fetch.an.liasse_xml import import_liasse_xml

    # Let's import the parent amendement
    amendements, errors = import_liasse_xml(
        open_liasse("liasse_only_parent.xml"), lecture_essoc
    )
    assert len(amendements) == 1
    assert amendements[0].num == 28
    assert amendements[0].parent is None
    assert errors == []

    # Now let's import a liasse with only a child amendement
    amendements, errors = import_liasse_xml(
        open_liasse("liasse_only_child.xml"), lecture_essoc
    )
    assert len(amendements) == 1
    assert amendements[0].num == 26
    assert amendements[0].parent.num == 28
    assert errors == []


def test_import_liasse_second_part(app):
    from zam_repondeur.fetch.an.liasse_xml import import_liasse_xml, LectureDoesNotMatch
    from zam_repondeur.models import DBSession, Lecture

    with transaction.manager:
        part1 = Lecture.create(
            chambre="an",
            session="15",
            num_texte=806,
            partie=1,
            titre="Nouvelle lecture – Titre lecture",
            organe="PO744107",
            dossier_legislatif="Fonction publique : un Etat au service d'une société de confiance",  # noqa
        )
        part2 = Lecture.create(
            chambre="an",
            session="15",
            num_texte=806,
            partie=2,
            titre="Nouvelle lecture – Titre lecture",
            organe="PO744107",
            dossier_legislatif="Fonction publique : un Etat au service d'une société de confiance",  # noqa
        )

    DBSession.add(part2)

    with pytest.raises(LectureDoesNotMatch):
        import_liasse_xml(open_liasse("liasse_second_part.xml"), part1)

    amendements, errors = import_liasse_xml(
        open_liasse("liasse_second_part.xml"), part2
    )

    assert (len(amendements), len(errors)) == (3, 0)
    for amendement in amendements:
        assert amendement.lecture == part2


def test_import_liasse_xml_lecture_is_not_an(lecture_senat):
    from zam_repondeur.fetch.an.liasse_xml import import_liasse_xml, BadChambre

    with pytest.raises(BadChambre):
        import_liasse_xml(open_liasse("liasse.xml"), lecture_senat)


def test_import_liasse_xml_lecture_does_not_match(lecture_an):
    from zam_repondeur.fetch.an.liasse_xml import import_liasse_xml, LectureDoesNotMatch

    with pytest.raises(LectureDoesNotMatch):
        import_liasse_xml(open_liasse("liasse.xml"), lecture_an)


def _check_amendement_0(amendement):

    assert amendement.lecture.chambre == "an"
    assert amendement.lecture.session == "15"
    assert amendement.lecture.num_texte == 806
    assert amendement.lecture.organe == "PO744107"

    assert amendement.article.type == "article"
    assert amendement.article.num == "2"
    assert amendement.article.mult == ""
    assert amendement.article.pos == ""
    assert amendement.article.content == {}
    assert amendement.article.user_content.title == ""
    assert amendement.article.user_content.presentation == ""

    assert amendement.alinea == 24

    assert amendement.num == 28
    assert amendement.rectif == 0

    assert amendement.auteur == "Fabrice Brun"
    assert amendement.matricule == "PA718838"
    assert amendement.groupe == "Les Républicains"

    assert amendement.date_depot == date(2018, 6, 7)

    assert amendement.sort == ""

    assert amendement.position is None  # no order yet
    assert amendement.id_discussion_commune is None
    assert amendement.id_identique is None

    assert amendement.parent is None

    assert (
        amendement.corps
        == "<div>Cet amendement est en cours de traitement par les services de l'Assemblée.</div>"  # noqa
    )
    assert amendement.expose == ""

    assert amendement.resume is None

    assert amendement.user_content.avis is None
    assert amendement.user_content.objet is None
    assert amendement.user_content.reponse is None


def _check_amendement_1(amendement):

    assert amendement.lecture.chambre == "an"
    assert amendement.lecture.session == "15"
    assert amendement.lecture.num_texte == 806
    assert amendement.lecture.organe == "PO744107"

    assert amendement.article.type == "annexe"
    assert amendement.article.num == ""
    assert amendement.article.mult == ""
    assert amendement.article.pos == ""
    assert amendement.article.content == {}
    assert amendement.article.user_content.title == ""
    assert amendement.article.user_content.presentation == ""

    assert amendement.alinea == 12

    assert amendement.num == 26
    assert amendement.rectif == 0

    assert amendement.auteur == "Fabrice Brun"
    assert amendement.matricule == "PA718838"
    assert amendement.groupe == "Les Républicains"

    assert amendement.date_depot == date(2018, 6, 7)

    assert amendement.sort == "Retiré"

    assert amendement.position is None  # no order yet
    assert amendement.id_discussion_commune is None
    assert amendement.id_identique is None

    assert amendement.parent.num == 28
    assert amendement.parent.rectif == 0

    assert amendement.corps == (
        "<p>L’alinéa 12 est complété par l’alinéa suivant :</p>\n"
        "<p>« L’article préliminaire du projet de loi pour un état "
        "au service d’une société de confiance définit les objectifs "
        "de l’action publique à horizon 2022. Elle s’articule autour "
        "de l’affirmation de principes généraux d’organisation et d’action, "
        "lesquels nécessitent des compléments. »</p>"
    )
    assert amendement.expose == (
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

    assert amendement.user_content.avis is None
    assert amendement.user_content.objet is None
    assert amendement.user_content.reponse is None


def _check_amendement_gouvernemental(amendement):
    assert amendement.auteur == "LE GOUVERNEMENT"
    assert amendement.matricule is None
    assert amendement.groupe is None
    assert amendement.gouvernemental
