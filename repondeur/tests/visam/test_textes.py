def test_conseil_empty_textes(app, conseil_ccfp, user_david):
    resp = app.get("/conseils/ccfp-2020-04-01", user=user_david)

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    assert "Aucun texte pour l’instant." in resp.text


def test_conseil_with_texte(app, conseil_ccfp, lecture_conseil_ccfp, user_david):
    resp = app.get("/conseils/ccfp-2020-04-01", user=user_david)

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    assert len(resp.parser.css(".texte nav a")) == 1


def test_conseil_add_texte_form(app, conseil_ccfp, user_sgg):
    resp = app.get("/conseils/ccfp-2020-04-01/add", user=user_sgg)

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


def test_conseil_add_texte_non_admin(app, conseil_ccfp, user_david):
    resp = app.get("/conseils/ccfp-2020-04-01/add", user=user_david)

    assert resp.status_code == 302
    assert resp.location == "https://visam.test/"

    resp = resp.maybe_follow()

    assert resp.status_code == 200
    assert "L’accès à cette page est réservé aux personnes autorisées." in resp.text


def test_conseil_add_texte_submit(app, conseil_ccfp, user_sgg):
    from zam_repondeur.models import Article, DBSession, Dossier, Lecture, Texte

    resp = app.get("/conseils/ccfp-2020-04-01/add", user=user_sgg)
    form = resp.forms["add-texte"]
    form["titre"] = "Titre du texte"
    form["contenu"] = "Contenu du texte"
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

    article = DBSession.query(Article).one()
    assert article.content == {"001": "Contenu du texte"}
    assert str(article) == "Art. 1"
    assert article.lecture == lecture
