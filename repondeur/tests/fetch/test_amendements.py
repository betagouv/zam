import pytest

from zam_repondeur.models.chambre import Chambre


class TestRemoteSource:
    @pytest.mark.parametrize("chambre", [Chambre.CCFP, Chambre.CSFPE])
    def test_conseil_de_la_fonction_publique(self, chambre):
        from zam_repondeur.services.fetch.amendements import RemoteSource

        assert RemoteSource.get_remote_source_for_chambre(chambre, settings={}) is None
