import pytest
import transaction


@pytest.fixture
def dossier_plfss2019(db):
    from zam_repondeur.models import Dossier

    with transaction.manager:
        dossier = Dossier.create(
            uid="DLR5L15N36892",
            titre="Sécurité sociale : loi de financement 2019",
            slug="plfss-2019",
        )

    return dossier
