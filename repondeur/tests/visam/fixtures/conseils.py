from datetime import date

import pytest
import transaction


@pytest.fixture
def conseil_ccfp(db):
    from zam_repondeur.models import Chambre
    from zam_repondeur.visam.models import Conseil, Formation

    with transaction.manager:
        conseil = Conseil.create(
            chambre=Chambre.CCFP,
            formation=Formation.ASSEMBLEE_PLENIERE,
            date=date(2020, 4, 1),
        )

    return conseil
