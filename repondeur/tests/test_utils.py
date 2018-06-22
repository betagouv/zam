import pytest


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
    "input,previous,output", [("foo", "", "foo"), ("id.", "previous", "previous")]
)
def test_normalize_reponse(input, previous, output):
    from zam_repondeur.utils import normalize_reponse

    assert normalize_reponse(input, previous) == output
