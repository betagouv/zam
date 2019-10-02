from pathlib import Path

import pytest
import transaction
from webtest import Upload
from webtest.forms import File

pytestmark = pytest.mark.usefixtures("lecture_an")


def test_get_form(app, user_david):
    resp = app.get(
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/options/", user=user_david
    )

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    # Check the form
    assert resp.forms["backup-form"].method == "post"
    assert resp.forms["backup-form"].action == (
        "https://zam.test"
        "/dossiers/plfss-2018"
        "/lectures/an.15.269.PO717460"
        "/import_backup"
    )

    assert list(resp.forms["backup-form"].fields.keys()) == ["backup", "upload"]

    assert isinstance(resp.forms["backup-form"].fields["backup"][0], File)
    assert resp.forms["backup-form"].fields["upload"][0].attrs["type"] == "submit"


@pytest.mark.usefixtures("amendements_an", "article1_an")
class TestPostForm:
    def _get_upload_form(self, app, user, headers=None):
        return app.get(
            "/dossiers/plfss-2018/lectures/an.15.269.PO717460/options/",
            user=user,
            headers=headers,
        ).forms["backup-form"]

    def _upload_backup(self, app, filename, user, team=None):
        headers = {"X-Remote-User": team.name} if team is not None else None
        form = self._get_upload_form(app, user=user, headers=headers)
        path = Path(__file__).parent.parent / "sample_data" / filename
        form["backup"] = Upload("file.json", path.read_bytes())
        return form.submit(user=user, headers=headers)

    def test_upload_redirects_to_index(self, app, user_david, lecture_an_url):
        resp = self._upload_backup(app, "backup.json", user_david)

        assert resp.status_code == 302
        assert resp.location == f"https://zam.test{lecture_an_url}/amendements/"

    def test_upload_success_message(self, app, user_david):
        resp = self._upload_backup(app, "backup.json", user_david).follow()

        assert resp.status_code == 200
        assert "2 réponse(s) chargée(s) avec succès" in resp.text

    def test_upload_success_event(self, app, user_david, lecture_an):
        from zam_repondeur.models import DBSession

        with transaction.manager:
            DBSession.add(user_david)

        self._upload_backup(app, "backup.json", user_david).follow()

        DBSession.add(lecture_an)
        assert len(lecture_an.events) == 1
        assert lecture_an.events[0].render_summary() == (
            "<abbr title='david@exemple.gouv.fr'>David</abbr> "
            "a importé des réponses d’un fichier JSON."
        )

    def test_upload_updates_user_content(self, app, user_david):
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

        amendement = DBSession.query(Amendement).filter(Amendement.num == 999).first()
        assert amendement.user_content.avis is None
        assert amendement.user_content.objet is None
        assert amendement.user_content.reponse is None

        self._upload_backup(app, "backup.json", user_david)

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

    def test_upload_does_not_update_position(self, app, user_david):
        from zam_repondeur.models import DBSession, Amendement

        amendement = DBSession.query(Amendement).filter(Amendement.num == 666).first()
        assert amendement.position == 1

        amendement = DBSession.query(Amendement).filter(Amendement.num == 999).first()
        assert amendement.position == 2

        self._upload_backup(app, "backup.json", user_david)

        amendement = DBSession.query(Amendement).filter(Amendement.num == 666).first()
        assert amendement.position == 1

        amendement = DBSession.query(Amendement).filter(Amendement.num == 999).first()
        assert amendement.position == 2

    def test_upload_backup_with_comments(self, app, user_david):
        from zam_repondeur.models import DBSession, Amendement
        from zam_repondeur.models.events.amendement import CommentsAmendementModifie

        self._upload_backup(app, "backup_with_comments.json", user_david)

        amendement = DBSession.query(Amendement).filter(Amendement.num == 666).first()
        assert amendement.user_content.comments == "A comment"
        events = {type(event): event for event in amendement.events}
        assert CommentsAmendementModifie in events

        amendement = DBSession.query(Amendement).filter(Amendement.num == 999).first()
        assert amendement.user_content.comments is None
        events = {type(event): event for event in amendement.events}
        assert CommentsAmendementModifie not in events

    def test_upload_backup_with_affectation_to_unknown_user_without_team(
        self, app, user_david, team_zam
    ):
        from zam_repondeur.models import DBSession, Amendement
        from zam_repondeur.models.events.amendement import AmendementTransfere

        amendement = DBSession.query(Amendement).filter(Amendement.num == 666).first()
        assert amendement.user_table is None

        amendement = DBSession.query(Amendement).filter(Amendement.num == 999).first()
        assert amendement.user_table is None

        self._upload_backup(app, "backup_with_affectation_new.json", user_david)

        amendement = DBSession.query(Amendement).filter(Amendement.num == 666).first()
        assert amendement.user_table.user.email == "melodie@exemple.gouv.fr"
        assert amendement.user_table.user.name == "Mélodie"
        assert amendement.user_table.user.teams[0].pk == team_zam.pk
        events = {type(event): event for event in amendement.events}
        assert AmendementTransfere in events

        amendement = DBSession.query(Amendement).filter(Amendement.num == 999).first()
        assert amendement.user_table is None
        events = {type(event): event for event in amendement.events}
        assert AmendementTransfere not in events

    def test_upload_backup_with_affectation_to_unknown_user_with_team(
        self, app, lecture_an, user_david, team_zam
    ):
        from zam_repondeur.models import DBSession, Amendement, User
        from zam_repondeur.models.events.amendement import AmendementTransfere

        amendement = DBSession.query(Amendement).filter(Amendement.num == 666).first()
        assert amendement.user_table is None

        amendement = DBSession.query(Amendement).filter(Amendement.num == 999).first()
        assert amendement.user_table is None

        user_melodie = (
            DBSession.query(User).filter_by(email="melodie@exemple.gouv.fr").first()
        )
        assert user_melodie is None
        assert "melodie@exemple.gouv.fr" not in {user.email for user in team_zam.users}

        self._upload_backup(
            app, "backup_with_affectation_new.json", user=user_david, team=team_zam
        )

        DBSession.add(team_zam)
        DBSession.refresh(team_zam)

        # Check the new user was created
        user_melodie = (
            DBSession.query(User).filter_by(email="melodie@exemple.gouv.fr").first()
        )
        assert user_melodie is not None
        assert user_melodie.email == "melodie@exemple.gouv.fr"
        assert user_melodie.name == "Mélodie"

        # Check the new user was added to the team
        assert "melodie@exemple.gouv.fr" in {user.email for user in team_zam.users}
        assert user_melodie.teams == [team_zam]

        # Check the amendement is on the new user's table
        amendement = DBSession.query(Amendement).filter(Amendement.num == 666).first()
        assert amendement.user_table.user is user_melodie
        events = {type(event): event for event in amendement.events}
        assert AmendementTransfere in events

        amendement = DBSession.query(Amendement).filter(Amendement.num == 999).first()
        assert amendement.user_table is None
        events = {type(event): event for event in amendement.events}
        assert AmendementTransfere not in events

    def test_upload_updates_affectation(self, app, lecture_an, user_david, user_ronan):
        from zam_repondeur.models import DBSession, Amendement

        with transaction.manager:
            DBSession.add_all([user_david, user_ronan])
            amendement = (
                DBSession.query(Amendement).filter(Amendement.num == 666).first()
            )
            amendement.user_table = user_david.table_for(lecture_an)

        assert amendement.user_table.user.email == "david@exemple.gouv.fr"
        assert amendement.user_table.user.name == "David"

        amendement = DBSession.query(Amendement).filter(Amendement.num == 999).first()
        assert amendement.user_table is None

        self._upload_backup(app, "backup_with_affectation_existing.json", user_david)

        amendement = DBSession.query(Amendement).filter(Amendement.num == 666).first()
        assert amendement.user_table.user.email == "ronan@exemple.gouv.fr"
        assert (
            amendement.user_table.user.name == "Ronan"
        )  # Should not override the name of an existing user.

        amendement = DBSession.query(Amendement).filter(Amendement.num == 999).first()
        assert amendement.user_table is None

    def test_upload_backup_with_articles(self, app, user_david):
        from zam_repondeur.models import DBSession, Amendement

        resp = self._upload_backup(
            app, "backup_with_articles.json", user_david
        ).follow()

        assert resp.status_code == 200
        assert (
            "2 réponse(s) chargée(s) avec succès, 1 article(s) chargé(s) avec succès"
            in resp.text
        )

        amendement = DBSession.query(Amendement).filter(Amendement.num == 666).first()
        assert amendement.article.user_content.title == "Titre"
        assert amendement.article.user_content.presentation == "Présentation"

    def test_upload_response_for_unknown_amendement(self, app, user_david):
        resp = self._upload_backup(app, "backup_wrong_number.json", user_david).follow()

        assert resp.status_code == 200
        assert (
            "Le fichier de sauvegarde n’a pas pu être chargé pour 1 amendement(s)"
            in resp.text
        )

    def test_upload_missing_file(self, app, user_david):
        form = self._get_upload_form(app, user_david)

        resp = form.submit()

        assert resp.status_code == 302
        assert resp.location == (
            "https://zam.test"
            "/dossiers/plfss-2018"
            "/lectures/an.15.269.PO717460"
            "/options"
        )

        resp = resp.follow()

        assert resp.status_code == 200
        assert "Veuillez d’abord sélectionner un fichier" in resp.text


def test_post_form_from_export(
    app, lecture_an, lecture_an_url, article1_an, tmpdir, user_david
):
    from zam_repondeur.models import DBSession, Amendement, Article
    from zam_repondeur.services.import_export.json import export_json

    filename = str(tmpdir.join("test.json"))

    with transaction.manager:
        article1_an.user_content.title = "Titre"
        article1_an.user_content.presentation = "Présentation"
        [
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
        counter = export_json(lecture_an, filename, request={})

    assert counter["amendements"] == 2
    assert counter["articles"] == 1

    with transaction.manager:
        article1_an.user_content.title = ""
        article1_an.user_content.presentation = ""

    form = app.get(
        "/dossiers/plfss-2018/lectures/an.15.269.PO717460/options/", user=user_david
    ).forms["backup-form"]
    form["backup"] = Upload("file.json", Path(filename).read_bytes())

    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == f"https://zam.test{lecture_an_url}/amendements/"

    resp = resp.follow()

    assert resp.status_code == 200
    assert (
        "2 réponse(s) chargée(s) avec succès, 1 article(s) chargé(s) avec succès"
        in resp.text
    )

    article = DBSession.query(Article).filter(Article.num == "1").first()
    assert article.user_content.title == "Titre"
    assert article.user_content.presentation == "Présentation"
