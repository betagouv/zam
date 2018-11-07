import transaction

import pytest
from sqlalchemy.exc import IntegrityError

EXAMPLES = [
    ("", 0, 0, "0"),
    ("COM-1", 1, 0, "1"),
    ("COM-48 rect.", 48, 1, "48 rect."),
    ("CE208", 208, 0, "208"),
    ("CE|208", 208, 0, "208"),
    ("42", 42, 0, "42"),
    ("42 rect.", 42, 1, "42 rect."),
    ("42 rect. bis", 42, 2, "42 rect. bis"),
    ("42 rect. ter", 42, 3, "42 rect. ter"),
]


@pytest.mark.parametrize("text,num,rectif,disp", EXAMPLES)
def test_parse_num(text, num, rectif, disp):
    from zam_repondeur.models import Amendement

    assert Amendement.parse_num(text) == (num, rectif)


@pytest.mark.parametrize("text,num,rectif,disp", EXAMPLES)
def test_num_disp(lecture_senat, article1_senat, text, num, rectif, disp):
    from zam_repondeur.models import Amendement

    amendement = Amendement.create(
        lecture=lecture_senat,
        article=article1_senat,
        alinea="",
        num=num,
        rectif=rectif,
        auteur="M. Dupont",
        parent=None,
    )
    assert amendement.num_disp == disp


def test_amendement_parent_relationship(amendements_an):
    from zam_repondeur.models import DBSession, Amendement

    a, b = DBSession.query(Amendement).all()

    assert a.parent is None
    assert b.parent is None

    b.parent = a

    # Note: when updating a relationship, the foreign key is only updated on a flush
    DBSession.flush()
    assert b.parent_pk == a.pk


def test_amendement_unicity(amendements_an, article1av_an):
    from zam_repondeur.models import Amendement, DBSession

    existing = amendements_an[0]
    with transaction.manager, pytest.raises(IntegrityError) as error_info:
        Amendement.create(
            lecture=existing.lecture,
            num=existing.num,
            rectif=existing.rectif + 1,
            article=article1av_an,
            parent=None,
            observations="don't worry, this is an expected error",
        )
        DBSession.flush()
    assert "constraint" in error_info.value._message()


def test_amendement_identiques(amendements_an):
    from zam_repondeur.models import Amendement, DBSession

    amendement_666, amendement_999 = DBSession.query(Amendement).all()

    assert amendement_666.identiques == []
    assert amendement_999.identiques == []

    amendement_666.identique = True
    amendement_999.identique = True
    amendement_666.discussion_commune = 42
    amendement_999.discussion_commune = 42
    amendement_666.avis = "Sagesse"
    amendement_999.avis = "Sagesse"

    assert amendement_666.identiques == [amendement_999]
    assert amendement_999.identiques == [amendement_666]


def test_amendement_identiques_are_similaires(amendements_an):
    from zam_repondeur.models import Amendement, DBSession

    amendement_666, amendement_999 = DBSession.query(Amendement).all()

    assert amendement_666.identiques == []
    assert amendement_999.identiques == []

    amendement_666.identique = True
    amendement_999.identique = True
    amendement_666.discussion_commune = 42
    amendement_999.discussion_commune = 42
    amendement_666.avis = "Favorable"
    amendement_999.avis = "Favorable"

    assert amendement_666.identiques == [amendement_999]
    assert amendement_999.identiques == [amendement_666]
    assert amendement_666.identiques_are_similaires
    assert amendement_999.identiques_are_similaires


def test_amendement_identiques_are_similaires_reponses(amendements_an):
    from zam_repondeur.models import Amendement, DBSession

    amendement_666, amendement_999 = DBSession.query(Amendement).all()

    assert amendement_666.identiques == []
    assert amendement_999.identiques == []

    amendement_666.identique = True
    amendement_999.identique = True
    amendement_666.discussion_commune = 42
    amendement_999.discussion_commune = 42
    amendement_666.avis = "Favorable"
    amendement_999.avis = "Favorable"
    amendement_666.reponse = "Une réponse"
    amendement_999.reponse = "Une réponse"

    assert amendement_666.identiques == [amendement_999]
    assert amendement_999.identiques == [amendement_666]
    assert amendement_666.identiques_are_similaires
    assert amendement_999.identiques_are_similaires


def test_amendement_identiques_are_similaires_reponses_with_spaces(amendements_an):
    from zam_repondeur.models import Amendement, DBSession

    amendement_666, amendement_999 = DBSession.query(Amendement).all()

    assert amendement_666.identiques == []
    assert amendement_999.identiques == []

    amendement_666.identique = True
    amendement_999.identique = True
    amendement_666.discussion_commune = 42
    amendement_999.discussion_commune = 42
    amendement_666.avis = "Favorable"
    amendement_999.avis = "Favorable"
    amendement_666.reponse = "Une réponse"
    amendement_999.reponse = """
    Une
 réponse"""

    assert amendement_666.identiques == [amendement_999]
    assert amendement_999.identiques == [amendement_666]
    assert amendement_666.identiques_are_similaires
    assert amendement_999.identiques_are_similaires


def test_amendement_identiques_are_similaires_reponses_with_tags(amendements_an):
    from zam_repondeur.models import Amendement, DBSession

    amendement_666, amendement_999 = DBSession.query(Amendement).all()

    assert amendement_666.identiques == []
    assert amendement_999.identiques == []

    amendement_666.identique = True
    amendement_999.identique = True
    amendement_666.discussion_commune = 42
    amendement_999.discussion_commune = 42
    amendement_666.avis = "Favorable"
    amendement_999.avis = "Favorable"
    amendement_666.reponse = "Une réponse"
    amendement_999.reponse = """
    <p>Une
 réponse</p>"""

    assert amendement_666.identiques == [amendement_999]
    assert amendement_999.identiques == [amendement_666]
    assert amendement_666.identiques_are_similaires
    assert amendement_999.identiques_are_similaires


def test_amendement_identiques_are_not_similaires(amendements_an):
    from zam_repondeur.models import Amendement, DBSession

    amendement_666, amendement_999 = DBSession.query(Amendement).all()

    assert amendement_666.identiques == []
    assert amendement_999.identiques == []

    amendement_666.identique = True
    amendement_999.identique = True
    amendement_666.discussion_commune = 42
    amendement_999.discussion_commune = 42
    amendement_666.avis = "Favorable"
    amendement_999.avis = "Défavorable"

    assert amendement_666.identiques == [amendement_999]
    assert amendement_999.identiques == [amendement_666]
    assert not amendement_666.identiques_are_similaires
    assert not amendement_999.identiques_are_similaires


def test_amendement_identiques_are_not_similaires_reponses(amendements_an):
    from zam_repondeur.models import Amendement, DBSession

    amendement_666, amendement_999 = DBSession.query(Amendement).all()

    assert amendement_666.identiques == []
    assert amendement_999.identiques == []

    amendement_666.identique = True
    amendement_999.identique = True
    amendement_666.discussion_commune = 42
    amendement_999.discussion_commune = 42
    amendement_666.avis = "Favorable"
    amendement_999.avis = "Favorable"
    amendement_666.reponse = "Une réponse"
    amendement_999.reponse = "Une autre réponse"

    assert amendement_666.identiques == [amendement_999]
    assert amendement_999.identiques == [amendement_666]
    assert not amendement_666.identiques_are_similaires
    assert not amendement_999.identiques_are_similaires
