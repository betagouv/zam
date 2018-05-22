def test_num_int():
    from models import Amendement
    amendement = Amendement(
        article="1",
        alinea="",
        num="230 rect.",
        auteur="M. Dupont",
    )
    assert amendement.num_int == 230
