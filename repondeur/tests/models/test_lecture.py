class TestLectureToStr:
    def test_an_seance_publique(self):
        from zam_repondeur.models import Lecture

        lecture = Lecture(
            chambre="an",
            session="15",
            num_texte=269,
            titre="bla bla",
            organe="PO717460",
        )
        result = "Assemblée nationale, 15e législature, Séance publique, texte nº 269"
        assert str(lecture) == result

    def test_an_commission(self):
        from zam_repondeur.models import Lecture

        lecture = Lecture(
            chambre="an", session="15", num_texte=269, titre="bla bla", organe="PO59048"
        )
        result = (
            "Assemblée nationale, 15e législature, Commission des finances, "
            "texte nº 269"
        )
        assert str(lecture) == result

    def test_an_commission_speciale(self):
        from zam_repondeur.models import Lecture

        lecture = Lecture(
            chambre="an",
            session="15",
            num_texte=806,
            titre="bla bla",
            organe="PO744107",
        )
        result = (
            "Assemblée nationale, 15e législature, Commission spéciale sur la société "
            "de confiance, texte nº 806"
        )
        assert str(lecture) == result

    def test_senat_seance_publique(self):
        from zam_repondeur.models import Lecture

        lecture = Lecture(
            chambre="senat",
            session="2017-2018",
            num_texte=63,
            titre="bla bla",
            organe="PO78718",
        )
        result = "Sénat, session 2017-2018, Séance publique, texte nº 63"
        assert str(lecture) == result
