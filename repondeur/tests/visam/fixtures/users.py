from datetime import datetime

import pytest
import transaction


@pytest.fixture
def user_admin(db):
    from zam_repondeur.models import User

    with transaction.manager:
        return User.create(
            name="Admin user", email="user@admin.gouv.fr", admin_at=datetime.utcnow()
        )


@pytest.fixture
def user_gouvernement(user_david):
    return user_david


@pytest.fixture
def org_gouvernement(db):
    from zam_repondeur.models import DBSession
    from zam_repondeur.visam.models import Organisation

    with transaction.manager:
        organisation = Organisation(name="Gouvernement")
        DBSession.add(organisation)

    return organisation


@pytest.fixture
def org_cgt(db):
    from zam_repondeur.models import DBSession
    from zam_repondeur.visam.models import Organisation

    with transaction.manager:
        organisation = Organisation(name="CGT")
        DBSession.add(organisation)

    return organisation


@pytest.fixture
def user_ccfp(db, user_david, org_cgt):
    from zam_repondeur.models import DBSession, Chambre
    from zam_repondeur.visam.models import UserMembership

    with transaction.manager:
        user_membership = UserMembership(
            user=user_david, chambre=Chambre.CCFP, organisation=org_cgt
        )
        DBSession.add(user_membership)

    return user_david


@pytest.fixture
def user_csfpe(db, user_david, org_cgt):
    from zam_repondeur.models import DBSession, Chambre
    from zam_repondeur.visam.models import UserMembership

    with transaction.manager:
        user_membership = UserMembership(
            user=user_david, chambre=Chambre.CSFPE, organisation=org_cgt
        )
        DBSession.add(user_membership)

    return user_david
