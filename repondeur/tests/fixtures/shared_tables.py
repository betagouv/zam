import pytest
import transaction


@pytest.fixture
def shared_table_lecture_an(db, lecture_an):
    from zam_repondeur.models import SharedTable

    with transaction.manager:
        shared_table = SharedTable.create(titre="Test table", lecture=lecture_an)

    return shared_table
