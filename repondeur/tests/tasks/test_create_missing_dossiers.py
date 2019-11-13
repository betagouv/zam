from unittest.mock import patch

import pytest


class TestCreateMissingDossierAN:
    @pytest.fixture(autouse=True)
    def existing_dossier(self, db):
        from zam_repondeur.models import Dossier

        return Dossier.create(
            an_id="existant", titre="Titre initial", slug="titre-initial"
        )

    def test_new_dossier_is_added(self):
        from zam_repondeur.models import DBSession, Dossier
        from zam_repondeur.services.data import repository
        from zam_repondeur.services.fetch.an.dossiers.models import DossierRef
        from zam_repondeur.tasks.periodic import create_missing_dossiers_an

        assert DBSession.query(Dossier).filter_by(an_id="nouveau").first() is None

        repository.set_opendata_dossier_ref(
            DossierRef(
                uid="nouveau",
                titre="Titre nouveau",
                slug="titre-nouveau",
                an_url="",
                senat_url="",
                lectures=[],
            )
        )

        with patch.object(repository, "list_opendata_dossiers") as mock_list:
            mock_list.return_value = ["existant", "nouveau"]

            create_missing_dossiers_an()

        dossier = DBSession.query(Dossier).filter_by(an_id="nouveau").one()

        assert dossier.an_id == "nouveau"
        assert dossier.titre == "Titre nouveau"
        assert dossier.slug == "titre-nouveau"

    def test_existing_dossier_is_not_modified(self):
        from zam_repondeur.models import DBSession, Dossier
        from zam_repondeur.services.data import repository
        from zam_repondeur.services.fetch.an.dossiers.models import DossierRef
        from zam_repondeur.tasks.periodic import create_missing_dossiers_an

        repository.set_opendata_dossier_ref(
            DossierRef(
                uid="existant",
                titre="Nouveau titre",
                slug="nouveau-titre",
                an_url="",
                senat_url="",
                lectures=[],
            )
        )

        with patch.object(repository, "list_opendata_dossiers") as mock_list:
            mock_list.return_value = ["existant"]

            create_missing_dossiers_an()

        dossier = DBSession.query(Dossier).filter_by(an_id="existant").one()
        assert dossier.an_id == "existant"
        assert dossier.titre == "Titre initial"
        assert dossier.slug == "titre-initial"

    def test_new_dossier_with_identical_slug_gets_a_suffix(self):
        from zam_repondeur.models import DBSession, Dossier
        from zam_repondeur.services.data import repository
        from zam_repondeur.services.fetch.an.dossiers.models import DossierRef
        from zam_repondeur.tasks.periodic import create_missing_dossiers_an

        repository.set_opendata_dossier_ref(
            DossierRef(
                uid="nouveau",
                titre="Titre différent",
                slug="titre-initial",
                an_url="",
                senat_url="",
                lectures=[],
            )
        )

        with patch.object(repository, "list_opendata_dossiers") as mock_list:
            mock_list.return_value = ["existant", "nouveau"]

            create_missing_dossiers_an()

        dossier = DBSession.query(Dossier).filter_by(an_id="nouveau").one()

        assert dossier.an_id == "nouveau"
        assert dossier.titre == "Titre différent"
        assert dossier.slug == "titre-initial-2"

    def test_removed_dossier_is_not_deleted(self):
        from zam_repondeur.models import DBSession, Dossier
        from zam_repondeur.services.data import repository
        from zam_repondeur.tasks.periodic import create_missing_dossiers_an

        with patch.object(repository, "list_opendata_dossiers") as mock_list:
            mock_list.return_value = []

            create_missing_dossiers_an()

        assert DBSession.query(Dossier).filter_by(an_id="existant").first() is not None


class TestCreateMissingDossierSénat:
    @pytest.fixture(autouse=True)
    def existing_dossier(self, db):
        from zam_repondeur.models import Dossier

        return Dossier.create(
            senat_id="existant", titre="Titre initial", slug="titre-initial"
        )

    def test_new_dossier_is_added(self):
        from zam_repondeur.models import DBSession, Dossier
        from zam_repondeur.services.data import repository
        from zam_repondeur.services.fetch.an.dossiers.models import DossierRef
        from zam_repondeur.tasks.periodic import create_missing_dossiers_senat

        assert DBSession.query(Dossier).filter_by(senat_id="nouveau").first() is None

        repository.set_senat_scraping_dossier_ref(
            DossierRef(
                uid="",
                titre="Titre nouveau",
                slug="titre-nouveau",
                an_url="",
                senat_url="http://www.senat.fr/dossier-legislatif/nouveau.html",
                lectures=[],
            )
        )

        with patch.object(repository, "list_senat_scraping_dossiers") as mock_list:
            mock_list.return_value = ["existant", "nouveau"]

            create_missing_dossiers_senat()

        dossier = DBSession.query(Dossier).filter_by(senat_id="nouveau").one()

        assert dossier.senat_id == "nouveau"
        assert dossier.titre == "Titre nouveau"
        assert dossier.slug == "titre-nouveau"

    def test_existing_dossier_is_not_modified(self):
        from zam_repondeur.models import DBSession, Dossier
        from zam_repondeur.services.data import repository
        from zam_repondeur.services.fetch.an.dossiers.models import DossierRef
        from zam_repondeur.tasks.periodic import create_missing_dossiers_senat

        repository.set_senat_scraping_dossier_ref(
            DossierRef(
                uid="",
                titre="Nouveau titre",
                slug="nouveau-titre",
                an_url="",
                senat_url="http://www.senat.fr/dossier-legislatif/existant.html",
                lectures=[],
            )
        )

        with patch.object(repository, "list_senat_scraping_dossiers") as mock_list:
            mock_list.return_value = ["existant"]

            create_missing_dossiers_senat()

        dossier = DBSession.query(Dossier).filter_by(senat_id="existant").one()
        assert dossier.senat_id == "existant"
        assert dossier.titre == "Titre initial"
        assert dossier.slug == "titre-initial"

    def test_new_dossier_with_identical_slug_gets_a_suffix(self):
        from zam_repondeur.models import DBSession, Dossier
        from zam_repondeur.services.data import repository
        from zam_repondeur.services.fetch.an.dossiers.models import DossierRef
        from zam_repondeur.tasks.periodic import create_missing_dossiers_senat

        repository.set_senat_scraping_dossier_ref(
            DossierRef(
                uid="",
                titre="Titre différent",
                slug="titre-initial",
                an_url="",
                senat_url="http://www.senat.fr/dossier-legislatif/nouveau.html",
                lectures=[],
            )
        )

        with patch.object(repository, "list_senat_scraping_dossiers") as mock_list:
            mock_list.return_value = ["existant", "nouveau"]

            create_missing_dossiers_senat()

        dossier = DBSession.query(Dossier).filter_by(senat_id="nouveau").one()

        assert dossier.senat_id == "nouveau"
        assert dossier.titre == "Titre différent"
        assert dossier.slug == "titre-initial-2"

    def test_removed_dossier_is_not_deleted(self):
        from zam_repondeur.models import DBSession, Dossier
        from zam_repondeur.services.data import repository
        from zam_repondeur.tasks.periodic import create_missing_dossiers_senat

        with patch.object(repository, "list_senat_scraping_dossiers") as mock_list:
            mock_list.return_value = []

            create_missing_dossiers_senat()

        assert (
            DBSession.query(Dossier).filter_by(senat_id="existant").first() is not None
        )
