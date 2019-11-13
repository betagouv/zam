from datetime import date

import pytest
import transaction

# We need data about dossiers, texts and groups
pytestmark = pytest.mark.usefixtures("data_repository")


class TestLectureToStr:
    def test_an_seance_publique_15e_legislature(
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

    def test_an_seance_publique_14e_legislature(self, db):
        from zam_repondeur.models import (
            Chambre,
            Dossier,
            Lecture,
            Phase,
            Texte,
            TypeTexte,
        )

        dossier = Dossier.create(
            an_id="DLR5L14N33494",
            titre="Questions sociales et santé : modernisation de notre système de santé",  # noqa
            slug="sante",
        )
        texte = Texte.create(
            type_=TypeTexte.PROJET,
            chambre=Chambre.AN,
            legislature=14,
            numero=2302,
            date_depot=date(2014, 10, 15),
        )
        lecture = Lecture.create(
            phase=Phase.PREMIERE_LECTURE,
            dossier=dossier,
            texte=texte,
            titre="Première lecture – Titre lecture",
            organe="PO644420",
        )
        result = (
            "Assemblée nationale, 14e législature, Séance publique, Première lecture, "
            "texte nº\u00a02302"
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


class TestIdentiquesMap:
    def test_empty(self, lecture_an):
        from zam_repondeur.models import DBSession

        DBSession.add(lecture_an)
        assert lecture_an.identiques_map == {}

    def test_no_identiques(self, lecture_an, amendements_an):
        amdt_666, amdt_999 = amendements_an
        assert lecture_an.identiques_map == {666: {amdt_666}, 999: {amdt_999}}

    def test_identiques(self, lecture_an, amendements_an):
        amdt_666, amdt_999 = amendements_an
        amdt_666.id_identique = amdt_999.id_identique = 1234
        assert lecture_an.identiques_map == {
            666: {amdt_666, amdt_999},
            999: {amdt_666, amdt_999},
        }


class TestSimilairesMap:
    def test_empty(self, lecture_an):
        from zam_repondeur.models import DBSession

        DBSession.add(lecture_an)
        assert lecture_an.similaires_map == {}

    def test_no_reponses(self, lecture_an, amendements_an):
        from zam_repondeur.models import DBSession

        DBSession.add(lecture_an)
        amdt_666, amdt_999 = amendements_an
        assert lecture_an.similaires_map == {
            666: {amdt_666, amdt_999},
            999: {amdt_666, amdt_999},
        }

    def test_same_reponses(self, lecture_an, amendements_an):
        from zam_repondeur.models import DBSession, Amendement, Lecture

        with transaction.manager:
            amendements_an[0].user_content.reponse = "bla bla"
            amendements_an[1].user_content.reponse = "bla bla"
            DBSession.add_all(amendements_an)

        lecture_an = DBSession.query(Lecture).one()
        amdt_666 = DBSession.query(Amendement).filter_by(num=666).one()
        amdt_999 = DBSession.query(Amendement).filter_by(num=999).one()

        assert amdt_666.user_content.reponse_hash == amdt_999.user_content.reponse_hash

        assert lecture_an.similaires_map == {
            666: {amdt_666, amdt_999},
            999: {amdt_666, amdt_999},
        }

    def test_different_reponses(self, lecture_an, amendements_an):
        from zam_repondeur.models import DBSession, Amendement, Lecture

        with transaction.manager:
            amendements_an[0].user_content.reponse = "bla bla"
            amendements_an[1].user_content.reponse = "bli bli"
            DBSession.add_all(amendements_an)

        lecture_an = DBSession.query(Lecture).one()
        amdt_666 = DBSession.query(Amendement).filter_by(num=666).one()
        amdt_999 = DBSession.query(Amendement).filter_by(num=999).one()

        assert amdt_666.user_content.reponse_hash != amdt_999.user_content.reponse_hash

        assert lecture_an.similaires_map == {666: {amdt_666}, 999: {amdt_999}}
