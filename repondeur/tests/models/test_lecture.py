import pytest

# We need data about dossiers, texts and groups
pytestmark = pytest.mark.usefixtures("data_repository")


class TestLectureToStr:
    def test_an_seance_publique(
        self, dossier_plfss2018, texte_plfss2018_an_premiere_lecture
    ):
        from zam_repondeur.models import Lecture, Phase

        lecture = Lecture.create(
            phase=Phase.PREMIERE_LECTURE,
            dossier=dossier_plfss2018,
            texte=texte_plfss2018_an_premiere_lecture,
            titre="Première lecture – Titre lecture",
            organe="PO717460",
        )
        result = (
            "Assemblée nationale, 15e législature, Séance publique, Première lecture, "
            "texte nº\u00a0269"
        )
        assert str(lecture) == result

    def test_an_commission(
        self, dossier_plfss2018, texte_plfss2018_an_premiere_lecture
    ):
        from zam_repondeur.models import Lecture, Phase

        lecture = Lecture.create(
            phase=Phase.PREMIERE_LECTURE,
            dossier=dossier_plfss2018,
            texte=texte_plfss2018_an_premiere_lecture,
            titre="Première lecture – Titre lecture",
            organe="PO59048",
        )
        result = (
            "Assemblée nationale, 15e législature, Commission des finances, "
            "de l'économie générale et du contrôle budgétaire, "
            "Première lecture, texte nº\u00a0269"
        )
        assert str(lecture) == result

    def test_an_commission_speciale(
        self, dossier_essoc2018, texte_essoc2018_an_nouvelle_lecture_commission_fond
    ):
        from zam_repondeur.models import Lecture, Phase

        lecture = Lecture.create(
            phase=Phase.NOUVELLE_LECTURE,
            dossier=dossier_essoc2018,
            texte=texte_essoc2018_an_nouvelle_lecture_commission_fond,
            titre="Nouvelle lecture – Titre lecture",
            organe="PO744107",
        )
        result = (
            "Assemblée nationale, 15e législature, Commission spéciale chargée "
            "d'examiner le projet de loi pour un État au service d'une société "
            "de confiance, Nouvelle lecture, texte nº\u00a0806"
        )
        assert str(lecture) == result

    def test_senat_seance_publique(
        self, dossier_plfss2018, texte_plfss2018_senat_premiere_lecture
    ):
        from zam_repondeur.models import Lecture, Phase

        lecture = Lecture.create(
            phase=Phase.NOUVELLE_LECTURE,
            dossier=dossier_plfss2018,
            texte=texte_plfss2018_senat_premiere_lecture,
            titre="Nouvelle lecture – Titre lecture",
            organe="PO78718",
        )
        result = (
            "Sénat, session 2017-2018, Séance publique, Nouvelle lecture, "
            "texte nº\u00a063"
        )
        assert str(lecture) == result


class TestLectureShortName:
    def test_an_seance_publique(
        self, dossier_plfss2018, texte_plfss2018_an_premiere_lecture
    ):
        from zam_repondeur.models import Lecture, Phase

        lecture = Lecture.create(
            phase=Phase.PREMIERE_LECTURE,
            dossier=dossier_plfss2018,
            texte=texte_plfss2018_an_premiere_lecture,
            titre="Première lecture – Titre lecture",
            organe="PO717460",
        )
        assert lecture.short_name == "AN, 1re lecture, séance publique"

    def test_an_commission(
        self, dossier_plfss2018, texte_plfss2018_an_premiere_lecture
    ):
        from zam_repondeur.models import Lecture, Phase

        lecture = Lecture.create(
            phase=Phase.PREMIERE_LECTURE,
            dossier=dossier_plfss2018,
            texte=texte_plfss2018_an_premiere_lecture,
            titre="Première lecture – Titre lecture",
            organe="PO59048",
        )
        assert lecture.short_name == "AN, 1re lecture, Finances"

    def test_an_commission_speciale(
        self, dossier_essoc2018, texte_essoc2018_an_nouvelle_lecture_commission_fond
    ):
        from zam_repondeur.models import Lecture, Phase

        lecture = Lecture.create(
            phase=Phase.NOUVELLE_LECTURE,
            dossier=dossier_essoc2018,
            texte=texte_essoc2018_an_nouvelle_lecture_commission_fond,
            titre="Nouvelle lecture – Titre lecture",
            organe="PO744107",
        )
        assert (
            lecture.short_name
            == "AN, Nouvelle lecture, Commission spéciale sur la société de confiance"
        )

    # def test_senat_seance_publique(
    #     self, dossier_plfss2018, texte_plfss2018_senat_premiere_lecture
    # ):
    #     from zam_repondeur.models import Lecture, Phase

    #     lecture = Lecture.create(
    #         phase=Phase.NOUVELLE_LECTURE,
    #         dossier=dossier_plfss2018,
    #         texte=texte_plfss2018_senat_premiere_lecture,
    #         titre="Nouvelle lecture – Titre lecture",
    #         organe="PO78718",
    #     )
    #     result = (
    #         "Sénat, session 2017-2018, Séance publique, Nouvelle lecture, "
    #         "texte nº\u00a063"
    #     )
    #     assert str(lecture) == result
