import pytest


EXAMPLES = [
    ("42", 42, 0),
    ("42 rect.", 42, 1),
    ("42 rect. bis", 42, 2),
    ("42 rect. ter", 42, 3),
]


@pytest.mark.parametrize("text,num,rectif", EXAMPLES)
def test_parse_num(text, num, rectif):
    from zam_repondeur.fetch.models import Amendement

    assert Amendement.parse_num(text) == (num, rectif)


@pytest.mark.parametrize("text,num,rectif", EXAMPLES)
def test_num_disp(text, num, rectif):
    from zam_repondeur.fetch.models import Amendement

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
    assert amendement.subdiv_disp == "Art. 1"


@pytest.mark.parametrize(
    "type_,pos,num,mult,output",
    [
        ("article", "", "1", "", "Art. 1"),
        ("annexe", "", "1", "", "Annexe 1"),
        ("article", "", "1", "bis", "Art. 1 bis"),
        ("article", "avant", "1", "", "Avant art. 1"),
    ],
)
def test_subdiv_disp(type_, pos, num, mult, output):
    from zam_repondeur.fetch.models import Amendement

    amendement = Amendement(
        chambre="senat",
        session="2017-2018",
        num_texte=63,
        organe="PO717460",
        subdiv_type=type_,
        subdiv_num=num,
        subdiv_mult=mult,
        subdiv_pos=pos,
        num=num,
    )
    assert amendement.subdiv_disp == output
