import pytest
import transaction


@pytest.mark.parametrize("input,output", [("1", 1), ("1\nfoo", 1), ("1,\nbar", 1)])
def test_normalize_num(input, output):
    from zam_repondeur.utils import normalize_num

    assert normalize_num(input) == output


@pytest.mark.parametrize(
    "input,output",
    [
        ("Favorable", "Favorable"),
        ("favorable", "Favorable"),
        ("Défavorable", "Défavorable"),
        ("DEFAVORABLE", "Défavorable"),
        ("Sagesse ", "Sagesse"),
        ("RETRAIT ", "Retrait"),
    ],
)
def test_normalize_avis(input, output):
    from zam_repondeur.utils import normalize_avis

    assert normalize_avis(input) == output


@pytest.mark.parametrize(
    "input,previous,lecture,output",
    [("foo", "", "", "foo"), ("id.", "previous", "", "previous")],
)
def test_normalize_reponse(input, previous, lecture, output):
    from zam_repondeur.utils import normalize_reponse

    assert normalize_reponse(input, previous, lecture) == output


def test_normalize_reponse_with_reference(app):
    from zam_repondeur.utils import normalize_reponse
    from zam_repondeur.models import DBSession, Amendement, Lecture

    with transaction.manager:
        lecture = Lecture.create(chambre="an", session="15", num_texte=269, titre="foo")
        amendement = Amendement(
            chambre="an",
            session="15",
            num_texte=269,
            subdiv_type="",
            subdiv_num="",
            num=91,
            reponse="reponse",
        )
        DBSession.add(amendement)

        assert normalize_reponse("id. 91 FOO", "", lecture) == amendement.reponse


def test_normalize_reponse_with_missing_reference(app):
    from zam_repondeur.utils import normalize_reponse
    from zam_repondeur.models import Lecture

    with transaction.manager:
        lecture = Lecture.create(chambre="an", session="15", num_texte=269, titre="foo")

        assert normalize_reponse("id. 91 FOO", "", lecture) == "id. 91 FOO"
