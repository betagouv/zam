import pytest


@pytest.fixture(autouse=True)
def existing_dossier(db):
    from zam_repondeur.models import Dossier

    return Dossier.create(uid="foo", titre="Titre initial", slug="titre-initial")


class TestCreateMissingDossier:
    def test_new_dossier_is_added(self):
        from zam_repondeur.fetch.an.dossiers.models import DossierRef
        from zam_repondeur.models import DBSession, Dossier
        from zam_repondeur.tasks.periodic import create_missing_dossiers

        assert DBSession.query(Dossier).filter_by(uid="bar").first() is None

        create_missing_dossiers(
            dossiers_by_uid={
                "bar": DossierRef(
                    uid="bar",
                    titre="Titre nouveau",
                    slug="titre-nouveau",
                    an_url="",
                    senat_url="",
                    lectures=[],
                )
            }
        )

        dossier = DBSession.query(Dossier).filter_by(uid="bar").one()

        assert dossier.uid == "bar"
        assert dossier.titre == "Titre nouveau"
        assert dossier.slug == "titre-nouveau"

    def test_existing_dossier_is_not_modified(self):
        from zam_repondeur.fetch.an.dossiers.models import DossierRef
        from zam_repondeur.models import DBSession, Dossier
        from zam_repondeur.tasks.periodic import create_missing_dossiers

        create_missing_dossiers(
            dossiers_by_uid={
                "foo": DossierRef(
                    uid="foo",
                    titre="Nouveau titre",
                    slug="nouveau-titre",
                    an_url="",
                    senat_url="",
                    lectures=[],
                )
            }
        )

        dossier = DBSession.query(Dossier).filter_by(uid="foo").one()
        assert dossier.uid == "foo"
        assert dossier.titre == "Titre initial"
        assert dossier.slug == "titre-initial"

    def test_new_dossier_with_identical_slug_gets_a_suffix(self):
        from zam_repondeur.fetch.an.dossiers.models import DossierRef
        from zam_repondeur.models import DBSession, Dossier
        from zam_repondeur.tasks.periodic import create_missing_dossiers

        create_missing_dossiers(
            dossiers_by_uid={
                "bar": DossierRef(
                    uid="bar",
                    titre="Titre différent",
                    slug="titre-initial",
                    an_url="",
                    senat_url="",
                    lectures=[],
                )
            }
        )

        dossier = DBSession.query(Dossier).filter_by(uid="bar").one()

        assert dossier.uid == "bar"
        assert dossier.titre == "Titre différent"
        assert dossier.slug == "titre-initial-2"

    def test_removed_dossier_is_not_deleted(self):
        from zam_repondeur.models import DBSession, Dossier
        from zam_repondeur.tasks.periodic import create_missing_dossiers

        create_missing_dossiers(dossiers_by_uid={})

        assert DBSession.query(Dossier).filter_by(uid="foo").first() is not None
