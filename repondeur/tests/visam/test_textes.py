from pathlib import Path

import pytest


def test_conseil_empty_textes(app, conseil_ccfp, user_david):
    resp = app.get("/conseils/ccfp-2020-04-01", user=user_david)

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    assert "Aucun texte pour l’instant." in resp.text
    assert "Ajouter un texte" in resp.text


def test_conseil_with_texte(app, conseil_ccfp, lecture_conseil_ccfp, user_david):
    resp = app.get("/conseils/ccfp-2020-04-01", user=user_david)

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    assert len(resp.parser.css(".texte nav a")) == 1
    assert "Ajouter un texte" in resp.text


def test_conseil_add_texte_form(app, conseil_ccfp, user_david):
    resp = app.get("/conseils/ccfp-2020-04-01/add", user=user_david)

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    # Check the form
    form = resp.forms["add-texte"]
    assert form.method == "POST"
    assert form.action == "/conseils/ccfp-2020-04-01/add"

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


def test_conseil_add_texte_submit(app, conseil_ccfp, contenu, user_david):
    from zam_repondeur.models import Article, DBSession, Dossier, Lecture, Texte

    resp = app.get("/conseils/ccfp-2020-04-01/add", user=user_david)
    form = resp.forms["add-texte"]
    form["titre"] = "Titre du texte"
    form["contenu"] = contenu

    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == (
        "https://visam.test/dossiers/titre-texte"
        "/lectures/ccfp..1.Assembl%C3%A9e%20pl%C3%A9ni%C3%A8re/amendements/"
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


def test_conseil_add_texte_submit_existing_same_conseil(
    app, conseil_ccfp, contenu, user_david
):
    resp = app.get("/conseils/ccfp-2020-04-01/add", user=user_david)
    form = resp.forms["add-texte"]
    form["titre"] = "Titre du texte"
    form["contenu"] = contenu

    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == (
        "https://visam.test/dossiers/titre-texte"
        "/lectures/ccfp..1.Assembl%C3%A9e%20pl%C3%A9ni%C3%A8re/amendements/"
    )

    resp = resp.follow()

    assert resp.status_code == 200
    assert "Texte créé avec succès." in resp.text

    resp = app.get("/conseils/ccfp-2020-04-01/add", user=user_david)
    form = resp.forms["add-texte"]
    form["titre"] = "Titre du texte"
    form["contenu"] = contenu

    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == (
        "https://visam.test/dossiers/titre-texte"
        "/lectures/ccfp..1.Assembl%C3%A9e%20pl%C3%A9ni%C3%A8re/amendements/"
    )

    resp = resp.follow()

    assert resp.status_code == 200
    assert "Ce texte existe déjà dans ce conseil…" in resp.text


def test_conseil_add_texte_submit_existing_different_conseil(
    app, conseil_ccfp, conseil_csfpe, contenu, user_david
):
    resp = app.get("/conseils/ccfp-2020-04-01/add", user=user_david)
    form = resp.forms["add-texte"]
    form["titre"] = "Titre du texte"
    form["contenu"] = contenu

    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == (
        "https://visam.test/dossiers/titre-texte"
        "/lectures/ccfp..1.Assembl%C3%A9e%20pl%C3%A9ni%C3%A8re/amendements/"
    )

    resp = resp.follow()

    assert resp.status_code == 200
    assert "Texte créé avec succès." in resp.text

    resp = app.get("/conseils/csfpe-2020-05-15/add", user=user_david)
    form = resp.forms["add-texte"]
    form["titre"] = "Titre du texte"
    form["contenu"] = contenu

    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == (
        "https://visam.test/dossiers/titre-texte"
        "/lectures/csfpe..1.Assembl%C3%A9e%20pl%C3%A9ni%C3%A8re/amendements/"
    )

    resp = resp.follow()

    assert resp.status_code == 200
    assert "Texte créé avec succès." in resp.text
