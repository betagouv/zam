import pytest
import transaction


@pytest.fixture
def user_ccfp(db, user_david):
    from zam_repondeur.models import DBSession, Chambre
    from zam_repondeur.visam.models import UserChambreMembership

    with transaction.manager:
        user_chambre = UserChambreMembership(user=user_david, chambre=Chambre.CCFP)
        DBSession.add(user_chambre)

    return user_david


@pytest.fixture
def user_csfpe(db, user_david):
    from zam_repondeur.models import DBSession, Chambre
    from zam_repondeur.visam.models import UserChambreMembership

    with transaction.manager:
        user_chambre = UserChambreMembership(user=user_david, chambre=Chambre.CSFPE)
        DBSession.add(user_chambre)

    return user_david
