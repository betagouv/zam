class TestMergeDossiers():
    def test_merge_empty_dossiers(self):
        from zam_repondeur.fetch.an.dossiers.models import DossierRef

        assert DossierRef.merge_dossiers({}, {}) == {}

    def test_merge_dossiers_and_empty(self):
        from zam_repondeur.fetch.an.dossiers.models import DossierRef

        dossiers1 = {"a": DossierRef("a", "titre1", [])}
        assert DossierRef.merge_dossiers(dossiers1, {}) == dossiers1

    def test_merge_empty_and_dossiers(self):
        from zam_repondeur.fetch.an.dossiers.models import DossierRef

        dossiers1 = {"a": DossierRef("a", "titre1", [])}
        assert DossierRef.merge_dossiers({}, dossiers1) == dossiers1
