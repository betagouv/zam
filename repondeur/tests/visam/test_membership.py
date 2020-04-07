def test_membership_default(user_david):
    from zam_repondeur.models import DBSession

    DBSession.add(user_david)

    assert user_david.chambres == []


def test_membership_with_chambre(user_ccfp):
    from zam_repondeur.models import Chambre, DBSession

    DBSession.add(user_ccfp)

    assert user_ccfp.chambres == [Chambre.CCFP]
