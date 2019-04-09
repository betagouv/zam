import transaction
from pathlib import Path

import pytest
from webtest import Upload
from webtest.forms import File


pytestmark = pytest.mark.usefixtures("lecture_an")


def test_get_form(app, user_david):
    resp = app.get("/lectures/an.15.269.PO717460/options/", user=user_david)

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    # Check the form
    assert resp.forms["import-form"].method == "post"
    assert (
        resp.forms["import-form"].action
        == "https://zam.test/lectures/an.15.269.PO717460/import_csv"
    )

    assert list(resp.forms["import-form"].fields.keys()) == ["reponses", "upload"]

    assert isinstance(resp.forms["import-form"].fields["reponses"][0], File)
    assert resp.forms["import-form"].fields["upload"][0].attrs["type"] == "submit"


TEST_FILES = ["reponses.csv", "reponses_semicolumns.csv", "reponses_with_bom.csv"]


@pytest.mark.usefixtures("amendements_an")
class TestPostForm:
    def _get_upload_form(self, app, user, headers=None):
        return app.get(
            "/lectures/an.15.269.PO717460/options/", user=user, headers=headers
        ).forms["import-form"]

    def _upload_csv(self, app, filename, user, team=None):
        headers = {"X-Remote-User": team.name} if team is not None else None
        form = self._get_upload_form(app, user=user, headers=headers)
        path = Path(__file__).parent / "sample_data" / filename
        form["reponses"] = Upload("file.csv", path.read_bytes())
        return form.submit(user=user, headers=headers)

    @pytest.mark.parametrize("filename", TEST_FILES)
    def test_upload_redirects_to_index(self, app, filename, user_david):
        resp = self._upload_csv(app, filename, user=user_david)

        assert resp.status_code == 302
        assert (
            resp.location == "https://zam.test/lectures/an.15.269.PO717460/amendements/"
        )

    @pytest.mark.parametrize("filename", TEST_FILES)
    def test_upload_success_message(self, app, filename, user_david):
        resp = self._upload_csv(app, filename, user=user_david).follow()

        assert resp.status_code == 200
        assert "2 réponse(s) chargée(s) avec succès" in resp.text

    @pytest.mark.parametrize("filename", TEST_FILES)
    def test_upload_updates_user_content(self, app, filename, user_david):
        from zam_repondeur.models import DBSession, Amendement
        from zam_repondeur.models.events.amendement import (
            AvisAmendementModifie,
            ObjetAmendementModifie,
            ReponseAmendementModifiee,
        )

        amendement = DBSession.query(Amendement).filter(Amendement.num == 666).first()
        assert amendement.user_content.avis is None
        assert amendement.user_content.objet is None
        assert amendement.user_content.reponse is None
        assert amendement.events == []

        amendement = DBSession.query(Amendement).filter(Amendement.num == 999).first()
        assert amendement.user_content.avis is None
        assert amendement.user_content.objet is None
        assert amendement.user_content.reponse is None
        assert amendement.events == []

        self._upload_csv(app, filename, user=user_david)

        amendement = DBSession.query(Amendement).filter(Amendement.num == 666).first()
        assert amendement.user_content.avis == "Défavorable"
        assert "<strong>ipsum</strong>" in amendement.user_content.objet
        assert "<blink>amet</blink>" not in amendement.user_content.objet

        assert "<i>tempor</i>" in amendement.user_content.reponse
        assert "<u>aliqua</u>" not in amendement.user_content.reponse

        events = {type(event): event for event in amendement.events}
        assert AvisAmendementModifie in events
        assert ObjetAmendementModifie in events
        assert ReponseAmendementModifiee in events

        amendement = DBSession.query(Amendement).filter(Amendement.num == 999).first()
        assert amendement.user_content.objet.startswith("Lorem")
        events = {type(event): event for event in amendement.events}
        assert ObjetAmendementModifie in events

    @pytest.mark.parametrize("filename", TEST_FILES)
    def test_upload_does_not_update_position(self, app, filename, user_david):
        from zam_repondeur.models import DBSession, Amendement

        amendement = DBSession.query(Amendement).filter(Amendement.num == 666).first()
        assert amendement.position == 1

        amendement = DBSession.query(Amendement).filter(Amendement.num == 999).first()
        assert amendement.position == 2

        self._upload_csv(app, filename, user=user_david)

        amendement = DBSession.query(Amendement).filter(Amendement.num == 666).first()
        assert amendement.position == 1

        amendement = DBSession.query(Amendement).filter(Amendement.num == 999).first()
        assert amendement.position == 2

    @pytest.mark.parametrize("filename", TEST_FILES)
    def test_upload_updates_modification_date(
        self, app, lecture_an, filename, user_david
    ):
        from zam_repondeur.models import Lecture

        with transaction.manager:
            initial_modified_at = lecture_an.modified_at

        self._upload_csv(app, filename, user=user_david)

        lecture = Lecture.get(
            chambre=lecture_an.chambre,
            session_or_legislature=lecture_an.session,
            num_texte=lecture_an.texte.numero,
            partie=None,
            organe=lecture_an.organe,
        )
        assert lecture.modified_at != initial_modified_at

    def test_upload_with_comments(self, app, user_david):
        from zam_repondeur.models import DBSession, Amendement
        from zam_repondeur.models.events.amendement import CommentsAmendementModifie

        self._upload_csv(app, "reponses_with_comments.csv", user=user_david)

        amendement = DBSession.query(Amendement).filter(Amendement.num == 666).first()
        assert amendement.user_content.comments == "A comment"
        events = {type(event): event for event in amendement.events}
        assert CommentsAmendementModifie in events

        amendement = DBSession.query(Amendement).filter(Amendement.num == 999).first()
        assert amendement.user_content.comments is None
        events = {type(event): event for event in amendement.events}
        assert CommentsAmendementModifie not in events

    def test_upload_with_affectation_to_unknown_user_without_team(
        self, app, user_david
    ):
        from zam_repondeur.models import DBSession, Amendement
        from zam_repondeur.models.events.amendement import AmendementTransfere

        amendement = DBSession.query(Amendement).filter(Amendement.num == 666).first()
        assert amendement.user_table is None

        amendement = DBSession.query(Amendement).filter(Amendement.num == 999).first()
        assert amendement.user_table is None

        self._upload_csv(app, "reponses_with_affectation.csv", user=user_david)

        amendement = DBSession.query(Amendement).filter(Amendement.num == 666).first()
        assert amendement.user_table.user.email == "david@larlet.fr"
        assert amendement.user_table.user.name == "David2"
        events = {type(event): event for event in amendement.events}
        assert AmendementTransfere in events

        amendement = DBSession.query(Amendement).filter(Amendement.num == 999).first()
        assert amendement.user_table is None
        events = {type(event): event for event in amendement.events}
        assert AmendementTransfere not in events

    def test_upload_with_affectation_to_unknown_user_with_team(
        self, app, lecture_an, user_ronan, team_zam
    ):
        from zam_repondeur.models import DBSession, Amendement, User
        from zam_repondeur.models.events.amendement import AmendementTransfere

        with transaction.manager:
            lecture_an.owned_by_team = team_zam
            DBSession.add(user_ronan)
            user_ronan.teams.append(team_zam)

        amendement = DBSession.query(Amendement).filter(Amendement.num == 666).first()
        assert amendement.user_table is None

        amendement = DBSession.query(Amendement).filter(Amendement.num == 999).first()
        assert amendement.user_table is None

        user_david2 = DBSession.query(User).filter_by(email="david@larlet.fr").first()
        assert user_david2 is None
        assert "david@larlet.fr" not in {user.email for user in team_zam.users}

        self._upload_csv(
            app, "reponses_with_affectation.csv", user=user_ronan, team=team_zam
        )

        DBSession.add(team_zam)
        DBSession.refresh(team_zam)

        # Check the new user was created
        user_david2 = DBSession.query(User).filter_by(email="david@larlet.fr").first()
        assert user_david2 is not None
        assert user_david2.email == "david@larlet.fr"
        assert user_david2.name == "David2"

        # Check the new user was added to the team
        assert "david@larlet.fr" in {user.email for user in team_zam.users}
        assert user_david2.teams == [team_zam]

        # Check the amendement is on the new user's table
        amendement = DBSession.query(Amendement).filter(Amendement.num == 666).first()
        assert amendement.user_table.user is user_david2
        events = {type(event): event for event in amendement.events}
        assert AmendementTransfere in events

        amendement = DBSession.query(Amendement).filter(Amendement.num == 999).first()
        assert amendement.user_table is None
        events = {type(event): event for event in amendement.events}
        assert AmendementTransfere not in events

    def test_upload_with_affectation_to_known_user(self, app, user_david):
        from zam_repondeur.models import DBSession, Amendement
        from zam_repondeur.models.events.amendement import AmendementTransfere

        with transaction.manager:
            DBSession.add(user_david)

        self._upload_csv(app, "reponses_with_affectation.csv", user=user_david)

        amendement = DBSession.query(Amendement).filter(Amendement.num == 666).first()
        assert amendement.user_table.user.email == "david@larlet.fr"
        assert amendement.user_table.user.name == "David2"
        events = {type(event): event for event in amendement.events}
        assert AmendementTransfere in events

        amendement = DBSession.query(Amendement).filter(Amendement.num == 999).first()
        assert amendement.user_table is None
        events = {type(event): event for event in amendement.events}
        assert AmendementTransfere not in events

    def test_upload_wrong_columns_names(self, app, user_david):
        resp = self._upload_csv(
            app, "reponses_wrong_columns_names.csv", user=user_david
        ).follow()

        assert resp.status_code == 200
        assert (
            "2 réponse(s) n’ont pas pu être chargée(s). Pour rappel, il faut que le "
            "fichier CSV contienne au moins les noms de colonnes suivants « Num amdt »"
            ", « Avis du Gouvernement », « Objet amdt » et « Réponse »." in resp.text
        )

    def test_upload_missing_file(self, app, user_david):
        form = self._get_upload_form(app, user=user_david)
        resp = form.submit()

        assert resp.status_code == 302
        assert resp.location == "https://zam.test/lectures/an.15.269.PO717460/options"

        resp = resp.follow()

        assert resp.status_code == 200
        assert "Veuillez d’abord sélectionner un fichier" in resp.text


def test_post_form_from_export(app, lecture_an, article1_an, tmpdir, user_david):
    from zam_repondeur.export.spreadsheet import write_csv
    from zam_repondeur.models import DBSession, Amendement

    filename = str(tmpdir.join("test.csv"))

    with transaction.manager:
        amendements = [
            Amendement.create(
                lecture=lecture_an,
                article=article1_an,
                num=num,
                position=position,
                avis="Favorable",
                objet="Un objet très pertinent",
                reponse="Une réponse très appropriée",
                comments="Avec des commentaires",
            )
            for position, num in enumerate((333, 777), 1)
        ]
        counter = write_csv(lecture_an, filename, request={})

    assert counter["amendements"] == 2

    with transaction.manager:
        amendements[0].user_content.avis = None
        amendements[1].user_content.avis = None

    form = app.get("/lectures/an.15.269.PO717460/options/", user=user_david).forms[
        "import-form"
    ]
    form["reponses"] = Upload("file.csv", Path(filename).read_bytes())

    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == "https://zam.test/lectures/an.15.269.PO717460/amendements/"

    resp = resp.follow()

    assert resp.status_code == 200
    assert "2 réponse(s) chargée(s) avec succès" in resp.text

    amendement = DBSession.query(Amendement).filter(Amendement.num == 333).first()
    assert amendement.user_content.avis == "Favorable"
    amendement = DBSession.query(Amendement).filter(Amendement.num == 777).first()
    assert amendement.user_content.avis == "Favorable"
