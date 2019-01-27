import pytest


@pytest.mark.parametrize(
    "text,type_,num,mult,pos",
    [
        ("", "", "", "", ""),
        ("Intitulé du projet de loi", "titre", "", "", ""),
        ("TITRE III : Un dispositif d'évaluation renouvelé", "section", "III", "", ""),
        ("Article liminaire", "article", "0", "", ""),
        ("Article 1", "article", "1", "", ""),
        ("Article 1er bis", "article", "1", "bis", ""),
        ("Article PREMIER", "article", "1", "", ""),
        (
            "Article 1er - Annexe (Stratégie nationale d'orientation de l'action publique)",  # noqa
            "article",
            "1",
            "",
            "",
        ),
        ("Article 8\xa0bis", "article", "8", "bis", ""),
        ("art. add. après Article 7", "article", "7", "", "après"),
        ("art. add. avant Article 39", "article", "39", "", "avant"),
        (
            "Article(s) additionnel(s) après Article 15 ter",
            "article",
            "15",
            "ter",
            "après",
        ),
        ("Article 31 (précédemment examiné)", "article", "31", "", ""),
        ("Annexe", "annexe", "", "", ""),
        ("ANNEXE B", "annexe", "B", "", ""),
        ("Section 2", "section", "2", "", ""),
        ("Soussection 2", "sous-section", "2", "", ""),
        ("Sous-section 2", "sous-section", "2", "", ""),
        ("Sous-section 2 : extras", "sous-section", "2", "", ""),
        ("Chapitre III", "chapitre", "III", "", ""),
        ("Article Article 3 bis AAA", "article", "3", "bis", ""),
        ("Article additionnel après l'article 13", "article", "13", "", "après"),
        ("div. add. après Article 13", "article", "13", "", "après"),
        ("Motions", "motion", "", "", ""),
        ("art. add. après Article 44(nouveau)", "article", "44", "", "après"),
        ("AVANT  L'ARTICLE 12", "article", "12", "", "avant"),
        ("APRÈS L'ARTICLE 12", "article", "12", "", "après"),
        ("APRES L'ARTICLE 12", "article", "12", "", "après"),
        ("Article 54 bis B", "article", "54", "bis B", ""),
        ("Article 55 septdecies", "article", "55", "septdecies", ""),
        ("Articles 55 septdecies à 55 novodecies", "article", "55", "septdecies", ""),
    ],
)
def test_parse_subdiv(text, type_, num, mult, pos):
    from zam_repondeur.fetch.division import _parse_subdiv

    assert _parse_subdiv(text) == (type_, num, mult, pos)
