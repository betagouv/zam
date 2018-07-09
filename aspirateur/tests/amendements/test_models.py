import pytest


EXAMPLES = [
    ("42", 42, 0),
    ("42 rect.", 42, 1),
    ("42 rect. bis", 42, 2),
    ("42 rect. ter", 42, 3),
]


@pytest.mark.parametrize("text,num,rectif", EXAMPLES)
def test_parse_num(text, num, rectif):
    from zam_aspirateur.amendements.models import Amendement

    assert Amendement.parse_num(text) == (num, rectif)


@pytest.mark.parametrize("text,num,rectif", EXAMPLES)
def test_num_disp(text, num, rectif):
    from zam_aspirateur.amendements.models import Amendement

    amendement = Amendement(
        chambre="senat",
        session="2017-2018",
        num_texte=63,
        organe="PO717460",
        subdiv_type="article",
        subdiv_num="1",
        alinea="",
        num=num,
        rectif=rectif,
        auteur="M. Dupont",
    )
    assert amendement.num_disp == text
