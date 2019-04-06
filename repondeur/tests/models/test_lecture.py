import pytest


# We need data about dossiers, texts and groups
pytestmark = pytest.mark.usefixtures("data_repository")


class TestLectureToStr:
    def test_an_seance_publique(self, texte_an):
        from zam_repondeur.models import Lecture

        lecture = Lecture(
            chambre="an",
            session="15",
            texte=texte_an,
            titre="Nouvelle lecture – Titre lecture",
            organe="PO717460",
        )
        result = (
            "Assemblée nationale, 15e législature, Séance publique, Nouvelle lecture, "
            "texte nº\u00a0269"
        )
        assert str(lecture) == result

    def test_an_commission(self, texte_an):
        from zam_repondeur.models import Lecture

        lecture = Lecture(
            chambre="an",
            session="15",
            texte=texte_an,
            titre="Nouvelle lecture – Titre lecture",
            organe="PO59048",
        )
        result = (
            "Assemblée nationale, 15e législature, Commission des finances, "
            "Nouvelle lecture, texte nº\u00a0269"
        )
        assert str(lecture) == result

    def test_an_commission_speciale(self, texte_commission_speciale):
        from zam_repondeur.models import Lecture

        lecture = Lecture(
            chambre="an",
            session="15",
            texte=texte_commission_speciale,
            titre="Nouvelle lecture – Titre lecture",
            organe="PO744107",
        )
        result = (
            "Assemblée nationale, 15e législature, Commission spéciale sur la société "
            "de confiance, Nouvelle lecture, texte nº\u00a0806"
        )
        assert str(lecture) == result

    def test_senat_seance_publique(self, texte_senat):
        from zam_repondeur.models import Lecture

        lecture = Lecture(
            chambre="senat",
            session="2017-2018",
            texte=texte_senat,
            titre="Nouvelle lecture – Titre lecture",
            organe="PO78718",
        )
        result = (
            "Sénat, session 2017-2018, Séance publique, Nouvelle lecture, "
            "texte nº\u00a063"
        )
        assert str(lecture) == result
