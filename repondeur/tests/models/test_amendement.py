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
