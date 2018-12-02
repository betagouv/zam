import transaction
from pathlib import Path

from webtest import Upload
from webtest.forms import File


def test_get_form(app, lecture_an):
    resp = app.get("/lectures/an.15.269.PO717460/amendements/")

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    # Check the form
    assert resp.forms["backup-form"].method == "post"
    assert resp.forms["backup-form"].action == ""

    assert list(resp.forms["backup-form"].fields.keys()) == ["backup", "upload"]

    assert isinstance(resp.forms["backup-form"].fields["backup"][0], File)
    assert resp.forms["backup-form"].fields["upload"][0].attrs["type"] == "submit"


def test_post_form(app, lecture_an, amendements_an, tmpdir):
    from zam_repondeur.models import DBSession, Amendement

    form = app.get("/lectures/an.15.269.PO717460/amendements/").forms["backup-form"]
    path = Path(__file__).parent / "sample_data" / "backup.json"
    form["backup"] = Upload("file.json", path.read_bytes())

    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == "http://localhost/lectures/an.15.269.PO717460/amendements/"

    resp = resp.follow()

    assert resp.status_code == 200
    assert "2 réponse(s) chargée(s) avec succès" in resp.text

    amendement = DBSession.query(Amendement).filter(Amendement.num == 666).first()
    assert amendement.avis == "Défavorable"
    assert amendement.position == 1
    assert "<strong>ipsum</strong>" in amendement.observations
    assert "<blink>amet</blink>" not in amendement.observations

    assert "<i>tempor</i>" in amendement.reponse
    assert "<u>aliqua</u>" not in amendement.reponse

    amendement = DBSession.query(Amendement).filter(Amendement.num == 999).first()
    assert amendement.observations.startswith("Lorem")
    assert amendement.position == 2


def test_post_form_updates_modification_date(app, lecture_an, amendements_an):
    from zam_repondeur.models import Lecture

    with transaction.manager:
        initial_modified_at = lecture_an.modified_at

    form = app.get("/lectures/an.15.269.PO717460/amendements/").forms["backup-form"]
    path = Path(__file__).parent / "sample_data" / "backup.json"
    form["backup"] = Upload("file.json", path.read_bytes())
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


def test_post_form_with_comments(app, lecture_an, amendements_an):
    from zam_repondeur.models import DBSession, Amendement

    form = app.get("/lectures/an.15.269.PO717460/amendements/").forms["backup-form"]
    path = Path(__file__).parent / "sample_data" / "backup_with_comments.json"
    form["backup"] = Upload("file.json", path.read_bytes())

    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == "http://localhost/lectures/an.15.269.PO717460/amendements/"

    resp = resp.follow()

    assert resp.status_code == 200
    assert "2 réponse(s) chargée(s) avec succès" in resp.text

    amendement = DBSession.query(Amendement).filter(Amendement.num == 666).first()
    assert amendement.position == 1
    assert amendement.comments == "A comment"

    amendement = DBSession.query(Amendement).filter(Amendement.num == 999).first()
    assert amendement.position == 2
    assert amendement.comments == ""


def test_post_form_with_affectations(app, lecture_an, amendements_an):
    from zam_repondeur.models import DBSession, Amendement

    form = app.get("/lectures/an.15.269.PO717460/amendements/").forms["backup-form"]
    path = Path(__file__).parent / "sample_data" / "backup_with_affectations.json"
    form["backup"] = Upload("file.json", path.read_bytes())

    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == "http://localhost/lectures/an.15.269.PO717460/amendements/"

    resp = resp.follow()

    assert resp.status_code == 200
    assert "2 réponse(s) chargée(s) avec succès" in resp.text

    amendement = DBSession.query(Amendement).filter(Amendement.num == 666).first()
    assert amendement.position == 1
    assert amendement.affectation == "Bureau"

    amendement = DBSession.query(Amendement).filter(Amendement.num == 999).first()
    assert amendement.position == 2
    assert amendement.affectation == ""


def test_post_form_with_articles(app, lecture_an, article1_an, amendements_an):
    from zam_repondeur.models import DBSession, Amendement

    form = app.get("/lectures/an.15.269.PO717460/amendements/").forms["backup-form"]
    path = Path(__file__).parent / "sample_data" / "backup_with_articles.json"
    form["backup"] = Upload("file.json", path.read_bytes())

    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == "http://localhost/lectures/an.15.269.PO717460/amendements/"

    resp = resp.follow()

    assert resp.status_code == 200
    assert (
        "2 réponse(s) chargée(s) avec succès, 1 article(s) chargé(s) avec succès"
        in resp.text
    )

    amendement = DBSession.query(Amendement).filter(Amendement.num == 666).first()
    assert amendement.article.titre == "Titre"
    assert amendement.article.contenu == "Contenu"


def test_post_form_wrong_number(app, lecture_an, amendements_an):
    form = app.get("/lectures/an.15.269.PO717460/amendements").forms["backup-form"]
    path = Path(__file__).parent / "sample_data" / "backup_wrong_number.json"
    form["backup"] = Upload("file.json", path.read_bytes())

    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == "http://localhost/lectures/an.15.269.PO717460/amendements/"

    resp = resp.follow()

    assert resp.status_code == 200
    assert (
        "Le fichier de sauvegarde n’a pas pu être chargé pour 1 amendement(s)"
        in resp.text
    )


def test_post_form_reponse_no_file(app, lecture_an, amendements_an):

    form = app.get("/lectures/an.15.269.PO717460/amendements/").forms["backup-form"]
    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == "http://localhost/lectures/an.15.269.PO717460/amendements/"

    resp = resp.follow()

    assert resp.status_code == 200
    assert "Veuillez d’abord sélectionner un fichier" in resp.text


def test_post_form_from_export(app, lecture_an, article1_an, tmpdir):
    from zam_repondeur.models import DBSession, Amendement, Article
    from zam_repondeur.writer import write_json

    filename = str(tmpdir.join("test.json"))

    with transaction.manager:
        article1_an.titre = "Titre"
        [
            Amendement.create(
                lecture=lecture_an,
                article=article1_an,
                num=num,
                position=position,
                avis="Favorable",
                observations="Des observations très pertinentes",
                reponse="Une réponse très appropriée",
                comments="Avec des commentaires",
            )
            for position, num in enumerate((333, 777), 1)
        ]
        nb_rows = write_json(lecture_an, filename, request={})

    assert nb_rows == 2 + 1  # amendements + article

    with transaction.manager:
        article1_an.titre = ""

    form = app.get("/lectures/an.15.269.PO717460/amendements/").forms["backup-form"]
    form["backup"] = Upload("file.json", Path(filename).read_bytes())

    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == "http://localhost/lectures/an.15.269.PO717460/amendements/"

    resp = resp.follow()

    assert resp.status_code == 200
    assert (
        "2 réponse(s) chargée(s) avec succès, 1 article(s) chargé(s) avec succès"
        in resp.text
    )

    article = DBSession.query(Article).filter(Article.num == "1").first()
    assert article.titre == "Titre"
