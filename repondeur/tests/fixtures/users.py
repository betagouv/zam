from datetime import datetime

import pytest
import transaction


@pytest.fixture
def team_zam(db):
    from zam_repondeur.models import Team

    return Team.create(name="Zam")


@pytest.fixture
def user_david(db, team_zam):
    from zam_repondeur.models import DBSession, User

    with transaction.manager:
        DBSession.add(team_zam)
        user = User.create(name="David", email="david@exemple.gouv.fr")
        team_zam.users.append(user)

    return user


@pytest.fixture
def user_ronan(db):
    from zam_repondeur.models import User

    return User.create(name="Ronan", email="ronan@exemple.gouv.fr")


@pytest.fixture
def user_daniel(db):
    from zam_repondeur.models import User

    return User.create(name="Daniel", email="daniel@exemple.gouv.fr")


@pytest.fixture
def user_sgg(db):
    from zam_repondeur.models import User

    with transaction.manager:
        return User.create(
            name="SGG user", email="user@sgg.pm.gouv.fr", admin_at=datetime.utcnow()
        )


@pytest.fixture
def user_david_table_an(user_david, lecture_an):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(user_david)
        table = user_david.table_for(lecture_an)
        DBSession.add(table)

    return table


@pytest.fixture
def user_david_table_senat(user_david, lecture_senat):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(user_david)
        table = user_david.table_for(lecture_senat)
        DBSession.add(table)

    return table


@pytest.fixture
def user_ronan_table_an(user_ronan, lecture_an):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(user_ronan)
        table = user_ronan.table_for(lecture_an)
        DBSession.add(table)

    return table


@pytest.fixture
def user_daniel_table_an(user_daniel, lecture_an):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(user_daniel)
        table = user_daniel.table_for(lecture_an)
        DBSession.add(table)

    return table
