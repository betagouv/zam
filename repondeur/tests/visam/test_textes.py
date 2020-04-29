from datetime import datetime, timedelta
from pathlib import Path

import pytest
import transaction


def test_seance_empty_textes(app, seance_ccfp, user_ccfp):
    resp = app.get("/seances/ccfp-2020-04-01", user=user_ccfp)

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    assert "Aucun texte pour l’instant." in resp.text
    assert "Ajouter un texte" in resp.text


def test_seance_with_texte_after_deadline(
    app, seance_ccfp, lecture_seance_ccfp, user_ccfp
):
    assert seance_ccfp.date < datetime.utcnow().date()
    resp = app.get("/seances/ccfp-2020-04-01", user=user_ccfp)

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    textes = resp.parser.css(".texte nav a")
    assert len(textes) == 2
    assert textes[0].text().strip() == "Accéder à ce texte"
    assert textes[1].text().strip() == "Accéder au dérouleur"
    assert "Ajouter un texte" in resp.text


def test_seance_with_texte_before_deadline(
    app, seance_ccfp, lecture_seance_ccfp, user_ccfp
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        seance_ccfp.date = (datetime.utcnow() + timedelta(days=4 + 1)).date()
        DBSession.add(seance_ccfp)

    resp = app.get(f"/seances/{seance_ccfp.slug}", user=user_ccfp)

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    textes = resp.parser.css(".texte nav a")
    assert len(textes) == 1
    assert textes[0].text().strip() == "Accéder à ce texte"
    assert "Ajouter un texte" in resp.text


def test_seance_add_texte_form(app, seance_ccfp, user_ccfp):
    resp = app.get("/seances/ccfp-2020-04-01/add", user=user_ccfp)

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    # Check the form
    form = resp.forms["add-texte"]
    assert form.method == "POST"
    assert form.action == "/seances/ccfp-2020-04-01/add"

    assert list(form.fields.keys()) == [
        "titre",
        "contenu",
        "submit",
    ]
    assert form.fields["submit"][0].attrs["type"] == "submit"


SAMPLE_FILE = Path(__file__).parent / "projet_de_decret.html"


@pytest.fixture(scope="session")
def contenu():
    return SAMPLE_FILE.read_text()


def test_seance_add_texte_submit(app, seance_ccfp, contenu, user_ccfp):
    from zam_repondeur.models import (
        Article,
        DBSession,
        Dossier,
        Lecture,
        Texte,
    )

    resp = app.get("/seances/ccfp-2020-04-01/add", user=user_ccfp)
    form = resp.forms["add-texte"]
    form["titre"] = "Titre du texte"
    form["contenu"] = contenu

    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == (
        "https://visam.test/seances/ccfp-2020-04-01/textes/titre-texte/amendements/"
    )

    resp = resp.follow()

    assert resp.status_code == 200
    assert "Texte créé avec succès." in resp.text

    texte = DBSession.query(Texte).one()
    assert texte.chambre.value == "Conseil commun de la fonction publique"

    dossier = DBSession.query(Dossier).one()
    assert dossier.titre == "Titre du texte"
    assert dossier.team.name == "Zam"

    lecture = DBSession.query(Lecture).one()
    assert lecture.titre == "Première lecture – Assemblée plénière"
    assert lecture.dossier == dossier
    assert lecture.texte == texte

    articles = DBSession.query(Article).all()
    assert len(articles) == 2

    article1, article2 = articles

    assert article1.type == "article"
    assert article1.num == "1"
    assert article1.mult == ""
    assert article1.pos == ""
    assert article1.content == {
        "001": "<p>A l’article 2 du décret du 22 août 2008 susvisé, les lignes : "
        "&nbsp;</p>",
        "002": "<table>\n"
        "    \n"
        "    \n"
        "    \n"
        "    \n"
        "    \n"
        "    \n"
        "    <tbody>\n"
        "        <tr>\n"
        '            <td colspan="4">\n'
        "                <p>&nbsp;</p>\n"
        "                <p>Architectes et urbanistes de l’Etat en chef </p>\n"
        "            </td>\n"
        "        </tr>\n"
        "        <tr>\n"
        "            <td>\n"
        "                <p>&nbsp;</p>\n"
        "                <p>ES </p>\n"
        "            </td>\n"
        "            <td>\n"
        "                <p>&nbsp;</p>\n"
        "                <p>HEB bis </p>\n"
        "            </td>\n"
        "            <td>\n"
        "                <p>&nbsp;</p>\n"
        "                <p>HEB bis </p>\n"
        "            </td>\n"
        "            <td>\n"
        "                <p>&nbsp;</p>\n"
        "            </td>\n"
        "        </tr>\n"
        "    </tbody>\n"
        "</table>",
        "003": "<p>sont remplacées par les lignes : &nbsp;</p>",
        "004": "<table>\n"
        "    \n"
        "    \n"
        "    \n"
        "    \n"
        "    \n"
        "    \n"
        "    <tbody>\n"
        "        <tr>\n"
        '            <td colspan="4">\n'
        "                <p>&nbsp;</p>\n"
        "                <p>Architectes et urbanistes de l’Etat en chef </p>\n"
        "            </td>\n"
        "        </tr>\n"
        "        <tr>\n"
        "            <td>\n"
        "                <p>&nbsp;</p>\n"
        "                <p>8 </p>\n"
        "            </td>\n"
        "            <td>\n"
        "                <p>&nbsp;</p>\n"
        "                <p>HEB bis </p>\n"
        "            </td>\n"
        "            <td>\n"
        "                <p>&nbsp;</p>\n"
        "                <p>HEB bis</p>\n"
        "            </td>\n"
        "            <td>\n"
        "                <p>&nbsp;</p>\n"
        "            </td>\n"
        "        </tr>\n"
        "    </tbody>\n"
        "</table>",
    }

    assert article2.type == "article"
    assert article2.num == "2"
    assert article2.mult == ""
    assert article2.content == {
        "001": "<p>La ministre de la transition écologique et solidaire, le ministre "
        "de l’action et des comptes publics, le ministre de la culture et le "
        "secrétaire d’Etat auprès du ministre de l’action et des comptes "
        "publics sont chargés, chacun en ce qui le concerne, de l’exécution du "
        "présent décret, qui sera publié au Journal officiel de la République "
        "française.&nbsp;</p>"
    }


def test_seance_add_texte_submit_existing_same_seance(
    app, seance_ccfp, contenu, user_ccfp
):
    resp = app.get("/seances/ccfp-2020-04-01/add", user=user_ccfp)
    form = resp.forms["add-texte"]
    form["titre"] = "Titre du texte"
    form["contenu"] = contenu

    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == (
        "https://visam.test/seances/ccfp-2020-04-01/textes/titre-texte/amendements/"
    )

    resp = resp.follow()

    assert resp.status_code == 200
    assert "Texte créé avec succès." in resp.text

    resp = app.get("/seances/ccfp-2020-04-01/add", user=user_ccfp)
    form = resp.forms["add-texte"]
    form["titre"] = "Titre du texte"
    form["contenu"] = contenu

    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == (
        "https://visam.test/seances/ccfp-2020-04-01/textes/titre-texte/amendements/"
    )

    resp = resp.follow()

    assert resp.status_code == 200
    assert "Ce texte est déjà à l’ordre du jour de cette séance…" in resp.text


def test_seance_add_texte_submit_existing_different_seance(
    app, seance_ccfp, seance_csfpe, contenu, user_ccfp, user_csfpe
):
    resp = app.get("/seances/ccfp-2020-04-01/add", user=user_ccfp)
    form = resp.forms["add-texte"]
    form["titre"] = "Titre du texte"
    form["contenu"] = contenu

    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == (
        "https://visam.test/seances/ccfp-2020-04-01/textes/titre-texte/amendements/"
    )

    resp = resp.follow()

    assert resp.status_code == 200
    assert "Texte créé avec succès." in resp.text

    resp = app.get("/seances/csfpe-2020-05-15/add", user=user_csfpe)
    form = resp.forms["add-texte"]
    form["titre"] = "Titre du texte"
    form["contenu"] = contenu

    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == (
        "https://visam.test/seances/csfpe-2020-05-15/textes/titre-texte/amendements/"
    )

    resp = resp.follow()

    assert resp.status_code == 200
    assert "Texte créé avec succès." in resp.text


def test_seance_add_texte_submit_increase_order(
    app, seance_ccfp, lecture_seance_ccfp, contenu, user_ccfp
):
    from zam_repondeur.models import DBSession
    from zam_repondeur.visam.models import Seance

    resp = app.get("/seances/ccfp-2020-04-01/add", user=user_ccfp)
    form = resp.forms["add-texte"]
    form["titre"] = "Titre du texte ajouté"
    form["contenu"] = contenu

    resp = form.submit()
    resp = resp.maybe_follow()
    assert resp.status_code == 200
    assert "Texte créé avec succès." in resp.text

    # Le texte est ajouté à la fin
    seance_ccfp = DBSession.query(Seance).get(seance_ccfp.pk)
    assert [lecture.dossier.titre for lecture in seance_ccfp.lectures] == [
        "Titre du texte CCFP",
        "Titre du texte ajouté",
    ]


def test_seance_reorder_textes_unique_lecture(app, lecture_seance_ccfp, user_ccfp):
    resp = app.get("/seances/ccfp-2020-04-01", user=user_ccfp)
    assert resp.status_code == 200
    assert '<script src="https://visam.test/static/js/seance.js' not in resp.text


@pytest.mark.usefixtures("lecture_seance_ccfp", "lecture_seance_ccfp_2")
def test_seance_reorder_textes(app, seance_ccfp, user_ccfp):
    from zam_repondeur.models import DBSession
    from zam_repondeur.visam.models import Seance

    # Ordre initial des textes
    seance_ccfp = DBSession.query(Seance).get(seance_ccfp.pk)
    assert [lecture.dossier.titre for lecture in seance_ccfp.lectures] == [
        "Titre du texte CCFP",
        "Titre du texte CCFP 2",
    ]

    resp = app.get("/seances/ccfp-2020-04-01", user=user_ccfp)
    assert resp.status_code == 200
    assert '<script src="https://visam.test/static/js/seance.js' in resp.text

    assert resp.parser.css("h3")[0].text() == "Titre du texte CCFP"
    assert resp.parser.css("h3")[1].text() == "Titre du texte CCFP 2"

    resp = app.post_json(
        "/seances/ccfp-2020-04-01/order", {"order": ["2", "1"]}, user=user_ccfp
    )
    assert resp.status_code == 200
    assert resp.text == "{}"

    # L’ordre des textes est modifié
    seance_ccfp = DBSession.query(Seance).get(seance_ccfp.pk)
    assert [lecture.dossier.titre for lecture in seance_ccfp.lectures] == [
        "Titre du texte CCFP 2",
        "Titre du texte CCFP",
    ]

    resp = app.get("/seances/ccfp-2020-04-01", user=user_ccfp)
    assert resp.status_code == 200
    assert resp.parser.css("h3")[0].text() == "Titre du texte CCFP 2"
    assert resp.parser.css("h3")[1].text() == "Titre du texte CCFP"
