import transaction

import pytest
from sqlalchemy.exc import IntegrityError

EXAMPLES = [
    ("42", 42, 0),
    ("42 rect.", 42, 1),
    ("42 rect. bis", 42, 2),
    ("42 rect. ter", 42, 3),
]


@pytest.mark.parametrize("text,num,rectif", EXAMPLES)
def test_parse_num(text, num, rectif):
    from zam_repondeur.models import Amendement

    assert Amendement.parse_num(text) == (num, rectif)


@pytest.mark.parametrize("text,num,rectif", [("", 0, 0)])
def test_parse_num_empty(text, num, rectif):
    from zam_repondeur.models import Amendement

    assert Amendement.parse_num(text) == (num, rectif)


@pytest.mark.parametrize("text,num,rectif", [("COM-1", 1, 0), ("COM-48 rect.", 48, 1)])
def test_parse_num_commissions(text, num, rectif):
    from zam_repondeur.models import Amendement

    assert Amendement.parse_num(text) == (num, rectif)


@pytest.mark.parametrize("text,num,rectif", EXAMPLES)
def test_num_disp(lecture_senat, article1, text, num, rectif):
    from zam_repondeur.models import Amendement

    amendement = Amendement.create(
        lecture=lecture_senat,
        article=article1,
        alinea="",
        num=num,
        rectif=rectif,
        auteur="M. Dupont",
        parent=None,
    )
    assert amendement.num_disp == text


def test_amendement_parent_relationship(amendements_an):
    from zam_repondeur.models import DBSession, Amendement

    parent, child = DBSession.query(Amendement).all()
    assert child.parent is None
    child.parent = parent
    DBSession.add(child)
    assert child.parent.num == parent.num


def test_amendement_unicity(amendements_an, article1av):
    from zam_repondeur.models import Amendement, DBSession

    existing = amendements_an[0]
    with transaction.manager, pytest.raises(IntegrityError) as error_info:
        Amendement.create(
            lecture=existing.lecture,
            num=existing.num,
            rectif=existing.rectif,
            article=article1av,
            parent=None,
        )
        DBSession.flush()
    assert (
        "UNIQUE constraint failed: "
        "amendements.num, amendements.rectif, amendements.lecture_pk"
    ) in error_info.value._message()
