def test_membership_default(user_david):
    from zam_repondeur.models import DBSession

    DBSession.add(user_david)

    assert user_david.chambres == []


def test_membership_with_chambre(user_david):
    from zam_repondeur.models import DBSession, Chambre
    from zam_repondeur.visam.models import UserChambreMembership

    user_chambre = UserChambreMembership(user=user_david, chambre=Chambre.CSFPE)
    DBSession.add(user_chambre)

    assert user_david.chambres == [Chambre.CSFPE]
