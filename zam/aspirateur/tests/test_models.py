def test_num_int():
    from zam_aspirateur.models import Amendement
    amendement = Amendement(
        article="1",
        alinea="",
        num="230 rect.",
        auteur="M. Dupont",
    )
    assert amendement.num_int == 230
