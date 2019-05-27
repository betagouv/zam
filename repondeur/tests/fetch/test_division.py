import pytest

from zam_repondeur.models.division import SubDiv


@pytest.mark.parametrize(
    "text,num",
    [
        ("liminaire", "0"),
        ("premier", "1"),
        ("PREMIER", "1"),
        ("42", "42"),
        ("Ier", "Ier"),
        ("MCMLXXVI", "MCMLXXVI"),
        ("Z", "Z"),
    ],
)
def test_numero(text, num):
    from zam_repondeur.fetch.division import NUMERO

    assert NUMERO.parse(text) == num


@pytest.mark.parametrize("text,mult", [("bis", "bis"), ("tricies", "tricies")])
def test_multiplicatif(text, mult):
    from zam_repondeur.fetch.division import MULTIPLICATIF

    assert MULTIPLICATIF.parse(text) == mult


@pytest.mark.parametrize(
    "text,mult", [("bis", "bis"), ("AAA", "AAA"), ("bis AAA", "bis AAA")]
)
def test_mult_add(text, mult):
    from zam_repondeur.fetch.division import MULT_ADD

    assert MULT_ADD.parse(text) == mult


@pytest.mark.parametrize(
    "text,subdiv",
    [
        ("Articles 1 à 2", SubDiv.create(type_="article", num="1")),
        ("Articles 3 bis à 3 ter", SubDiv.create(type_="article", num="3", mult="bis")),
    ],
)
def test_intervalle(text, subdiv):
    from zam_repondeur.fetch.division import INTERVALLE

    assert INTERVALLE.parse(text) == subdiv


@pytest.mark.parametrize(
    "text,type_,num,mult,pos",
    [
        ("Article liminaire", "article", "0", "", ""),
        ("Article 1", "article", "1", "", ""),
        ("Article 1er bis", "article", "1", "bis", ""),
        ("Article PREMIER", "article", "1", "", ""),
        ("Article 31 (précédemment examiné)", "article", "31", "", ""),
        ("Article 39 (État B (crédits de la mission))", "article", "39", "", ""),
        ("Article 54 bis B", "article", "54", "bis B", ""),
        ("Article 42\xa0bis\xa0A\xa0", "article", "42", "bis A", ""),
        ("Article 55 septdecies", "article", "55", "septdecies", ""),
        ("Article 3 bis AAA", "article", "3", "bis AAA", ""),
        ("Article Article 3 bis AAA", "article", "3", "bis AAA", ""),
    ],
)
def test_parse_article(text, type_, num, mult, pos):
    from zam_repondeur.fetch.division import ARTICLE_UNIQUE

    assert ARTICLE_UNIQUE.parse(text) == SubDiv(type_, num, mult, pos)


@pytest.mark.parametrize(
    "text,type_,num,mult,pos",
    [
        ("art. add. avant TITRE Ier : BLA BLA", "section", "Ier", "", "avant"),
        ("art. add. avant TITRE III : BLA BLA", "section", "III", "", "avant"),
        ("art. add. avant Chapitre Ier : BLA BLA", "chapitre", "Ier", "", "avant"),
        ("art. add. après Article 7", "article", "7", "", "après"),
        ("art. add. après Article 26 (Supprimé)", "article", "26", "", "après"),
        (
            "art. add. après Article 32\xa0bis (précédemment examiné)",
            "article",
            "32",
            "bis",
            "après",
        ),
        ("art. add. avant Article 39", "article", "39", "", "avant"),
        (
            "Article(s) additionnel(s) après Article 15 ter",
            "article",
            "15",
            "ter",
            "après",
        ),
        ("Article additionnel après l'article 13", "article", "13", "", "après"),
        ("div. add. après Article 13", "article", "13", "", "après"),
        ("art. add. après Article 44(nouveau)", "article", "44", "", "après"),
        ("AVANT  L'ARTICLE 12", "article", "12", "", "avant"),
        ("APRÈS L'ARTICLE 12", "article", "12", "", "après"),
        ("APRES L'ARTICLE 12", "article", "12", "", "après"),
    ],
)
def test_parse_article_additionnel(text, type_, num, mult, pos):
    from zam_repondeur.fetch.division import ARTICLE_ADDITIONNEL

    assert ARTICLE_ADDITIONNEL.parse(text) == SubDiv(type_, num, mult, pos)


@pytest.mark.parametrize(
    "text,type_,num,mult,pos",
    [
        ("", "", "", "", ""),
        ("Intitulé de la proposition de loi", "titre", "", "", ""),
        ("Intitulé du projet de loi", "titre", "", "", ""),
        ("Intitulé du projet de loi constitutionnelle", "titre", "", "", ""),
        ("TITRE Ier : Bla bla", "section", "Ier", "", ""),
        ("TITRE III : Un dispositif d'évaluation renouvelé", "section", "III", "", ""),
        (
            "Article 1er - Annexe (Stratégie nationale d'orientation de l'action publique)",  # noqa
            "article",
            "1",
            "",
            "",
        ),
        ("Article 8\xa0bis", "article", "8", "bis", ""),
        ("Annexe", "annexe", "", "", ""),
        ("ANNEXE B", "annexe", "B", "", ""),
        ("Section 2", "section", "2", "", ""),
        ("Soussection 2", "sous-section", "2", "", ""),
        ("Sous-section 2", "sous-section", "2", "", ""),
        ("Sous-section 2 : extras", "sous-section", "2", "", ""),
        ("Chapitre IER : Bla bla", "chapitre", "Ier", "", ""),
        ("Chapitre III", "chapitre", "III", "", ""),
        ("Motions", "motion", "", "", ""),
        ("Articles 55 septdecies à 55 novodecies", "article", "55", "septdecies", ""),
        ("Article 52 à 54", "article", "52", "", ""),
        (
            "art. add. après Article additionnel après l'article 61 quinquies",
            "article",
            "61",
            "quinquies",
            "après",
        ),
    ],
)
def test_parse_subdiv(text, type_, num, mult, pos):
    from zam_repondeur.fetch.division import parse_subdiv

    assert parse_subdiv(text) == SubDiv(type_, num, mult, pos)


@pytest.mark.parametrize(
    "division",
    [
        "Projet de loi de financement de la sécurité sociale pour 2018",
        "PROJET DE LOI de financement de la sécurité sociale pour 2018",
    ],
)
def test_parse_subdiv_texte_title(texte_plfss2018_an_premiere_lecture, division):
    from zam_repondeur.fetch.division import parse_subdiv

    subdiv = parse_subdiv(division, texte=texte_plfss2018_an_premiere_lecture)
    assert subdiv == SubDiv("titre", "", "", "")


def test_parse_subdiv_art_add_av_texte_title(texte_plfss2018_an_premiere_lecture):
    from zam_repondeur.fetch.division import parse_subdiv

    subdiv = parse_subdiv(
        "art. add. avant PROJET DE LOI de financement de la sécurité sociale pour 2018",
        texte=texte_plfss2018_an_premiere_lecture,
    )
    assert subdiv == SubDiv("titre", "", "", "avant")


def test_parse_subdiv_error(texte_plfss2018_an_premiere_lecture):
    from zam_repondeur.fetch.division import parse_subdiv

    subdiv = parse_subdiv(
        "this is unparsable garbage", texte=texte_plfss2018_an_premiere_lecture
    )
    assert subdiv == SubDiv("erreur", "", "", "")
