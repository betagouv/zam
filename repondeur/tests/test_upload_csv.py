import transaction
from pathlib import Path

import pytest
from webtest import Upload
from webtest.forms import File


pytestmark = pytest.mark.usefixtures("lecture_an")


def test_get_form(app):
    resp = app.get("/lectures/an.15.269.PO717460/options/", user="user@example.com")

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


@pytest.mark.usefixtures("amendements_an")
class TestPostForm:
    def test_upload_redirects_to_index(self, app):
        form = app.get(
            "/lectures/an.15.269.PO717460/options/", user="user@example.com"
        ).forms["import-form"]
        path = Path(__file__).parent / "sample_data" / "reponses.csv"
        form["reponses"] = Upload("file.csv", path.read_bytes())

        resp = form.submit()

        assert resp.status_code == 302
        assert (
            resp.location == "https://zam.test/lectures/an.15.269.PO717460/amendements/"
        )

    def test_upload_success_message(self, app):
        form = app.get(
            "/lectures/an.15.269.PO717460/options/", user="user@example.com"
        ).forms["import-form"]
        path = Path(__file__).parent / "sample_data" / "reponses.csv"
        form["reponses"] = Upload("file.csv", path.read_bytes())

        resp = form.submit().follow()

        assert resp.status_code == 200
        assert "2 réponse(s) chargée(s) avec succès" in resp.text

    def test_upload_updates_user_content(self, app):
        from zam_repondeur.models import DBSession, Amendement

        amendement = DBSession.query(Amendement).filter(Amendement.num == 666).first()
        assert amendement.user_content.avis is None
        assert amendement.user_content.objet is None
        assert amendement.user_content.reponse is None

        amendement = DBSession.query(Amendement).filter(Amendement.num == 999).first()
        assert amendement.user_content.avis is None
        assert amendement.user_content.objet is None
        assert amendement.user_content.reponse is None

        form = app.get(
            "/lectures/an.15.269.PO717460/options/", user="user@example.com"
        ).forms["import-form"]
        path = Path(__file__).parent / "sample_data" / "reponses.csv"
        form["reponses"] = Upload("file.csv", path.read_bytes())

        form.submit().follow()

        amendement = DBSession.query(Amendement).filter(Amendement.num == 666).first()
        assert amendement.user_content.avis == "Défavorable"
        assert "<strong>ipsum</strong>" in amendement.user_content.objet
        assert "<blink>amet</blink>" not in amendement.user_content.objet

        assert "<i>tempor</i>" in amendement.user_content.reponse
        assert "<u>aliqua</u>" not in amendement.user_content.reponse

        amendement = DBSession.query(Amendement).filter(Amendement.num == 999).first()
        assert amendement.user_content.objet.startswith("Lorem")

    def test_upload_does_not_update_position(self, app):
        from zam_repondeur.models import DBSession, Amendement

        amendement = DBSession.query(Amendement).filter(Amendement.num == 666).first()
        assert amendement.position == 1

        amendement = DBSession.query(Amendement).filter(Amendement.num == 999).first()
        assert amendement.position == 2

        form = app.get(
            "/lectures/an.15.269.PO717460/options/", user="user@example.com"
        ).forms["import-form"]
        path = Path(__file__).parent / "sample_data" / "reponses.csv"
        form["reponses"] = Upload("file.csv", path.read_bytes())

        form.submit().follow()

        amendement = DBSession.query(Amendement).filter(Amendement.num == 666).first()
        assert amendement.position == 1

        amendement = DBSession.query(Amendement).filter(Amendement.num == 999).first()
        assert amendement.position == 2

    def test_upload_updates_modification_date(self, app, lecture_an):
        from zam_repondeur.models import Lecture

        with transaction.manager:
            initial_modified_at = lecture_an.modified_at

        form = app.get(
            "/lectures/an.15.269.PO717460/options/", user="user@example.com"
        ).forms["import-form"]
        path = Path(__file__).parent / "sample_data" / "reponses.csv"
        form["reponses"] = Upload("file.csv", path.read_bytes())
        form.submit()

        with transaction.manager:
            lecture = Lecture.get(
                chambre=lecture_an.chambre,
                session=lecture_an.session,
                num_texte=lecture_an.num_texte,
                partie=None,
                organe=lecture_an.organe,
            )
            assert lecture.modified_at != initial_modified_at

    def test_upload_semicolumns(self, app):
        from zam_repondeur.models import DBSession, Amendement

        form = app.get(
            "/lectures/an.15.269.PO717460/options/", user="user@example.com"
        ).forms["import-form"]
        path = Path(__file__).parent / "sample_data" / "reponses_semicolumns.csv"
        form["reponses"] = Upload("file.csv", path.read_bytes())

        form.submit().follow()

        amendement = DBSession.query(Amendement).filter(Amendement.num == 666).first()
        assert amendement.user_content.avis == "Défavorable"
        assert "<strong>ipsum</strong>" in amendement.user_content.objet
        assert "<blink>amet</blink>" not in amendement.user_content.objet

        assert "<i>tempor</i>" in amendement.user_content.reponse
        assert "<u>aliqua</u>" not in amendement.user_content.reponse

        amendement = DBSession.query(Amendement).filter(Amendement.num == 999).first()
        assert amendement.user_content.objet.startswith("Lorem")

    def test_upload_with_comments(self, app):
        from zam_repondeur.models import DBSession, Amendement

        form = app.get(
            "/lectures/an.15.269.PO717460/options/", user="user@example.com"
        ).forms["import-form"]
        path = Path(__file__).parent / "sample_data" / "reponses_with_comments.csv"
        form["reponses"] = Upload("file.csv", path.read_bytes())

        form.submit().follow()

        amendement = DBSession.query(Amendement).filter(Amendement.num == 666).first()
        assert amendement.user_content.comments == "A comment"

        amendement = DBSession.query(Amendement).filter(Amendement.num == 999).first()
        assert amendement.user_content.comments == ""

    def test_upload_with_affectation_unknown(self, app):
        from zam_repondeur.models import DBSession, Amendement

        form = app.get(
            "/lectures/an.15.269.PO717460/options/", user="user@example.com"
        ).forms["import-form"]
        path = Path(__file__).parent / "sample_data" / "reponses_with_affectation.csv"
        form["reponses"] = Upload("file.csv", path.read_bytes())

        form.submit().follow()

        amendement = DBSession.query(Amendement).filter(Amendement.num == 666).first()
        assert amendement.user_table.user.email == "david@larlet.fr"
        assert amendement.user_table.user.name == "David2"

        amendement = DBSession.query(Amendement).filter(Amendement.num == 999).first()
        assert amendement.user_table is None

    def test_upload_with_affectation_known(self, app, user_david):
        from zam_repondeur.models import DBSession, Amendement

        with transaction.manager:
            DBSession.add(user_david)

        form = app.get(
            "/lectures/an.15.269.PO717460/options/", user="user@example.com"
        ).forms["import-form"]
        path = Path(__file__).parent / "sample_data" / "reponses_with_affectation.csv"
        form["reponses"] = Upload("file.csv", path.read_bytes())

        form.submit().follow()

        amendement = DBSession.query(Amendement).filter(Amendement.num == 666).first()
        assert amendement.user_table.user.email == "david@larlet.fr"
        assert amendement.user_table.user.name == "David2"

        amendement = DBSession.query(Amendement).filter(Amendement.num == 999).first()
        assert amendement.user_table is None

    def test_upload_with_bom(self, app):
        form = app.get(
            "/lectures/an.15.269.PO717460/options/", user="user@example.com"
        ).forms["import-form"]
        path = Path(__file__).parent / "sample_data" / "reponses_with_bom.csv"
        form["reponses"] = Upload("file.csv", path.read_bytes())

        resp = form.submit().follow()

        assert resp.status_code == 200
        assert "2 réponse(s) chargée(s) avec succès" in resp.text

    def test_upload_wrong_columns_names(self, app):
        form = app.get(
            "/lectures/an.15.269.PO717460/options", user="user@example.com"
        ).forms["import-form"]
        path = (
            Path(__file__).parent / "sample_data" / "reponses_wrong_columns_names.csv"
        )
        form["reponses"] = Upload("file.csv", path.read_bytes())

        resp = form.submit().follow()

        assert resp.status_code == 200
        assert (
            "2 réponse(s) n’ont pas pu être chargée(s). Pour rappel, il faut que le "
            "fichier CSV contienne au moins les noms de colonnes suivants « Num amdt »"
            ", « Avis du Gouvernement », « Objet amdt » et « Réponse »." in resp.text
        )

    def test_upload_missing_file(self, app):

        form = app.get(
            "/lectures/an.15.269.PO717460/options/", user="user@example.com"
        ).forms["import-form"]
        resp = form.submit()

        assert resp.status_code == 302
        assert resp.location == "https://zam.test/lectures/an.15.269.PO717460/options"

        resp = resp.follow()

        assert resp.status_code == 200
        assert "Veuillez d’abord sélectionner un fichier" in resp.text


def test_post_form_from_export(app, lecture_an, article1_an, tmpdir):
    from zam_repondeur.models import DBSession, Amendement
    from zam_repondeur.writer import write_csv

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
        nb_rows = write_csv(lecture_an, filename, request={})

    assert nb_rows == 2

    with transaction.manager:
        amendements[0].user_content.avis = None
        amendements[1].user_content.avis = None

    form = app.get(
        "/lectures/an.15.269.PO717460/options/", user="user@example.com"
    ).forms["import-form"]
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
