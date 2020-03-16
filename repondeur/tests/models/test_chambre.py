import pytest

from zam_repondeur.models.chambre import Chambre


@pytest.mark.parametrize(
    "text,chambre",
    [
        ("an", Chambre.AN),
        ("senat", Chambre.SENAT),
        ("ccfp", Chambre.CCFP),
        ("csfpe", Chambre.CSFPE),
    ],
)
def test_chambre_from_string(text, chambre):
    assert Chambre.from_string(text) == chambre


def test_invalid_chambre():
    with pytest.raises(ValueError) as exc_info:
        Chambre.from_string("foo")
    assert str(exc_info.value) == "Invalid string value 'foo' for Chambre"
