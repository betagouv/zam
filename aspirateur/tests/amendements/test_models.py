def test_num_int():
    from zam_aspirateur.amendements.models import Amendement

    amendement = Amendement(
        chambre="senat",
        session="2017-2018",
        num_texte="63",
        subdiv_type="article",
        subdiv_num="1",
        alinea="",
        num="230 rect.",
        auteur="M. Dupont",
    )
    assert amendement.num_int == 230
