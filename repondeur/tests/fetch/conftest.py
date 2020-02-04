import pytest


@pytest.fixture(scope="session")
def source_senat(settings):
    from zam_repondeur.services.fetch.senat.amendements import Senat

    return Senat(settings=settings)


@pytest.fixture(scope="session")
def source_an(settings):
    from zam_repondeur.services.fetch.an.amendements import AssembleeNationale

    return AssembleeNationale(settings=settings)
