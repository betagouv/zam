from datetime import date

import pytest


@pytest.fixture(autouse=True)
def existing_texte(db):
    from zam_repondeur.models import Chambre, Texte, TypeTexte

    return Texte.create(
        type_=TypeTexte.PROJET,
        chambre=Chambre.AN,
        numero=123,
        date_depot=date(2019, 9, 6),
        legislature=15,
    )


class TestCreateMissingtexte:
    def test_new_texte_is_added(self):
        from zam_repondeur.fetch.an.dossiers.models import (
            DossierRef,
            LectureRef,
            TexteRef,
        )
        from zam_repondeur.models import Chambre, DBSession, Texte, TypeTexte
        from zam_repondeur.tasks.periodic import create_missing_textes

        assert (
            DBSession.query(Texte)
            .filter_by(chambre=Chambre.AN, numero=124, legislature=15)
            .first()
            is None
        )

        create_missing_textes(
            dossiers_by_uid={
                "foo": DossierRef(
                    uid="foo",
                    titre="Titre",
                    slug="titre",
                    an_url="",
                    senat_url="",
                    lectures=[
                        LectureRef(
                            chambre=Chambre.AN,
                            titre="bla bla",
                            organe="PO717460",
                            partie=None,
                            texte=TexteRef(
                                uid="bar",
                                type_=TypeTexte.PROJET,
                                chambre=Chambre.AN,
                                legislature=15,
                                numero=124,
                                titre_long="Titre long",
                                titre_court="Titre court",
                                date_depot=date(2019, 9, 6),
                            ),
                        )
                    ],
                )
            }
        )

        texte = (
            DBSession.query(Texte)
            .filter_by(chambre=Chambre.AN, numero=124, legislature=15)
            .one()
        )
        assert texte.type_ == TypeTexte.PROJET
        assert texte.date_depot == date(2019, 9, 6)

    def test_existing_texte_is_not_modified(self):
        from zam_repondeur.fetch.an.dossiers.models import (
            DossierRef,
            LectureRef,
            TexteRef,
        )
        from zam_repondeur.models import Chambre, DBSession, Texte, TypeTexte
        from zam_repondeur.tasks.periodic import create_missing_textes

        create_missing_textes(
            dossiers_by_uid={
                "foo": DossierRef(
                    uid="foo",
                    titre="Titre",
                    slug="titre",
                    an_url="",
                    senat_url="",
                    lectures=[
                        LectureRef(
                            chambre=Chambre.AN,
                            titre="bla bla",
                            organe="PO717460",
                            partie=None,
                            texte=TexteRef(
                                uid="bar",
                                type_=TypeTexte.PROPOSITION,
                                chambre=Chambre.AN,
                                legislature=15,
                                numero=123,
                                titre_long="Titre long",
                                titre_court="Titre court",
                                date_depot=date(2000, 1, 1),
                            ),
                        )
                    ],
                )
            }
        )

        texte = (
            DBSession.query(Texte)
            .filter_by(chambre=Chambre.AN, numero=123, legislature=15)
            .one()
        )
        assert texte.type_ == TypeTexte.PROJET
        assert texte.date_depot == date(2019, 9, 6)

    def test_removed_texte_is_not_deleted(self):
        from zam_repondeur.models import Chambre, DBSession, Texte
        from zam_repondeur.tasks.periodic import create_missing_textes

        assert (
            DBSession.query(Texte)
            .filter_by(chambre=Chambre.AN, numero=123, legislature=15)
            .first()
        ) is not None

        create_missing_textes(dossiers_by_uid={})

        assert (
            DBSession.query(Texte)
            .filter_by(chambre=Chambre.AN, numero=123, legislature=15)
            .first()
        ) is not None
