import pytest


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


@pytest.mark.parametrize(
    "type_,pos,num,mult,output",
    [
        ("article", "", "1", "", "Art. 1"),
        ("annexe", "", "1", "", "Annexe 1"),
        ("article", "", "1", "bis", "Art. 1 bis"),
        ("article", "avant", "1", "", "Avant art. 1"),
    ],
)
def test_article_disp(type_, pos, num, mult, output):
    from zam_repondeur.models import Article

    article = Article.create(type=type_, num=num, mult=mult, pos=pos)
    assert str(article) == output


class TestLectureToStr:
    def test_an_seance_publique(self):
        from zam_repondeur.models import Lecture

        lecture = Lecture(
            chambre="an",
            session="15",
            num_texte=269,
            titre="bla bla",
            organe="PO717460",
        )
        result = "Assemblée nationale, 15e législature, Séance publique, texte nº 269"
        assert str(lecture) == result

    def test_an_commission(self):
        from zam_repondeur.models import Lecture

        lecture = Lecture(
            chambre="an", session="15", num_texte=269, titre="bla bla", organe="PO59048"
        )
        result = (
            "Assemblée nationale, 15e législature, Commission des finances, "
            "texte nº 269"
        )
        assert str(lecture) == result

    def test_an_commission_speciale(self):
        from zam_repondeur.models import Lecture

        lecture = Lecture(
            chambre="an",
            session="15",
            num_texte=806,
            titre="bla bla",
            organe="PO744107",
        )
        result = (
            "Assemblée nationale, 15e législature, Commission spéciale sur la société "
            "de confiance, texte nº 806"
        )
        assert str(lecture) == result

    def test_senat_seance_publique(self):
        from zam_repondeur.models import Lecture

        lecture = Lecture(
            chambre="senat",
            session="2017-2018",
            num_texte=63,
            titre="bla bla",
            organe="PO78718",
        )
        result = "Sénat, session 2017-2018, Séance publique, texte nº 63"
        assert str(lecture) == result


def test_amendement_parent_relationship(amendements_an):
    from zam_repondeur.models import DBSession, Amendement

    parent, child = DBSession.query(Amendement).all()
    assert child.parent is None
    child.parent = parent
    DBSession.add(child)
    assert child.parent.num == parent.num
