import pytest

from zam_repondeur.models.division import SubDiv


@pytest.mark.parametrize(
    "text,num",
    [
        ("liminaire", "0"),
        ("unique", "1"),
        ("premier", "1"),
        ("PRÉLIMINAIRE", "PRÉLIMINAIRE"),
        ("PREMIER", "1"),
        ("1e", "1"),
        ("1er", "1"),
        ("1ère", "1"),
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
        ("1er quinquies", "article", "1", "quinquies", ""),
        ("Article 7\xa0", "article", "7", "", ""),
        ("Article 31 (précédemment examiné)", "article", "31", "", ""),
        (
            "Article 17 [examiné dans le cadre de la législation en commission]",
            "article",
            "17",
            "",
            "",
        ),
        ("Article 39 (État B (crédits de la mission))", "article", "39", "", ""),
        ("Article 54 bis B", "article", "54", "bis B", ""),
        ("Article 42\xa0bis\xa0A\xa0", "article", "42", "bis A", ""),
        ("Article 55 septdecies", "article", "55", "septdecies", ""),
        ("Article 3 bis AAA", "article", "3", "bis AAA", ""),
        ("Article Article 3 bis AAA", "article", "3", "bis AAA", ""),
        ("Article 20 bis (nouveau)", "article", "20", "bis", ""),
        ("Article 20 bis ( nouveau)", "article", "20", "bis", ""),
        ("Article 20 bis (nouveau", "article", "20", "bis", ""),
        ("Articles 104 ter", "article", "104", "ter", ""),
        ("Art. 53 (section 3)", "article", "53", "", ""),
        ("Art. 53 (ÉTAT D)", "article", "53", "", ""),
        ("Article 4 bis (section 3)", "article", "4", "bis", ""),
        ("Article 4 (ÉTAT D)", "article", "4", "", ""),
        ("Article 4 bis (ÉTAT D)", "article", "4", "bis", ""),
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
        ("art. add. avant CHAPITRE IER BLA BLA", "chapitre", "Ier", "", "avant"),
        ("art. add. avant CHAPITRE III  BLA BLA", "chapitre", "III", "", "avant"),
        ("art. add. avant Article unique", "article", "1", "", "avant"),
        ("art. add. après Article unique", "article", "1", "", "après"),
        ("art. add. après Article 7", "article", "7", "", "après"),
        ("art. add. après Article 7\xa0", "article", "7", "", "après"),
        (
            "art. add. après Article 12\xa0septies\xa0A\xa0",
            "article",
            "12",
            "septies A",
            "après",
        ),
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
        ("Articles additionnels après l'article 51", "article", "51", "", "après"),
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
        (
            "Projet de loi de financement de la sécurité sociale pour 2018",
            "titre",
            "",
            "",
            "",
        ),
        (
            "Projet de loi ratifiant l'ordonnance n° 2014-1090 du 26 septembre 2014 relative à la mise en accessibilité des établissements recevant du public, des transports publics, des bâtiments d'habitation et de la voirie pour les personnes handicapées",  # noqa
            "titre",
            "",
            "",
            "",
        ),
        (
            "PROJET DE LOI de financement de la sécurité sociale pour 2018",
            "titre",
            "",
            "",
            "",
        ),
        (
            "PROPOSITION DE LOIrelative à l'encadrement de l'utilisation du téléphone portable dans les écoles et les collèges",  # noqa
            "titre",
            "",
            "",
            "",
        ),
        ("Intitulé de la proposition de loi", "titre", "", "", ""),
        ("Intitulé de  la proposition de loi", "titre", "", "", ""),
        ("Intitulé de la PROPOSITION DE LOI", "titre", "", "", ""),
        ("Intitulé de la proposition de loi constitutionnelle", "titre", "", "", ""),
        ("Intitulé de la proposition de loi organique", "titre", "", "", ""),
        ("Intitulé du PROJET DE LOI", "titre", "", "", ""),
        ("Intitulé du projet de loi organique", "titre", "", "", ""),
        ("Intitulé du projet de loi", "titre", "", "", ""),
        ("Intitulé du projet de loi constitutionnelle", "titre", "", "", ""),
        ("Intitulé du texte", "titre", "", "", ""),
        ("TITRE PRÉLIMINAIRE", "section", "PRÉLIMINAIRE", "", ""),
        (
            "TITRE PRÉLIMINAIRE  DISPOSITIONS D'ORIENTATION ET DE PROGRAMMATION",
            "section",
            "PRÉLIMINAIRE",
            "",
            "",
        ),
        ("TITRE Ier : Bla bla", "section", "Ier", "", ""),
        ("TITRE II DISPOSITIONS FINANCIERES", "section", "II", "", ""),
        ("TITRE III : Un dispositif d'évaluation renouvelé", "section", "III", "", ""),
        (
            "Article 1er - Annexe (Stratégie nationale d'orientation de l'action publique)",  # noqa
            "article",
            "1",
            "",
            "",
        ),
        ("Article 8\xa0bis", "article", "8", "bis", ""),
        ("Article 1erbis (nouveau)", "article", "1", "bis", ""),
        ("Article 6ter (nouveau)", "article", "6", "ter", ""),
        ("Article 36 quinquiesA (nouveau)", "article", "36", "quinquies A", ""),
        ("Annexe", "annexe", "", "", ""),
        ("ANNEXE B", "annexe", "B", "", ""),
        (
            "Section 1  Le Haut Conseil de la famille et des âges de la vie",
            "section",
            "1",
            "",
            "",
        ),
        ("Section 1ère", "section", "1", "", ""),
        ("Section 2", "section", "2", "", ""),
        ("Soussection 2", "sous-section", "2", "", ""),
        ("Sous-section 2", "sous-section", "2", "", ""),
        ("Sous-section 2 : extras", "sous-section", "2", "", ""),
        ("Chapitre IER : Bla bla", "chapitre", "Ier", "", ""),
        (
            "CHAPITRE II  Renforcer la formation professionnelle et l'apprentissage",
            "chapitre",
            "II",
            "",
            "",
        ),
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
        ("Article 56 bis İ", "article", "56", "bis I", ""),
    ],
)
def test_parse_subdiv(text, type_, num, mult, pos):
    from zam_repondeur.fetch.division import DIVISION

    assert DIVISION.parse(text) == SubDiv(type_, num, mult, pos)


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
