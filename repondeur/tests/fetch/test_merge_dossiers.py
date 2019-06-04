class TestMergeDossiers:
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

    def test_merge_different_dossiers(self):
        from zam_repondeur.fetch.an.dossiers.models import DossierRef

        dossiers1 = {"a": DossierRef("a", "titre1", [])}
        dossiers2 = {"b": DossierRef("b", "titre2", [])}
        assert DossierRef.merge_dossiers(dossiers1, dossiers2) == {
            "a": DossierRef("a", "titre1", []),
            "b": DossierRef("b", "titre2", []),
        }

    def test_merge_different_dossiers_reversed(self):
        from zam_repondeur.fetch.an.dossiers.models import DossierRef

        dossiers1 = {"a": DossierRef("a", "titre1", [])}
        dossiers2 = {"b": DossierRef("b", "titre2", [])}
        assert DossierRef.merge_dossiers(dossiers2, dossiers1) == {
            "a": DossierRef("a", "titre1", []),
            "b": DossierRef("b", "titre2", []),
        }

    def test_merge_same_dossier(self):
        from zam_repondeur.fetch.an.dossiers.models import DossierRef, LectureRef

        dossiers1 = {"a": DossierRef("a", "titre1", [LectureRef(...)])}
        dossiers2 = {"1": DossierRef("a", "titre2", [LectureRef(...)])}
        assert DossierRef.merge_dossiers(dossiers1, dossiers2) == {
            "a": DossierRef("a", "titre1", [...])
        }
