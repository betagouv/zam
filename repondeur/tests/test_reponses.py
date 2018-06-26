import transaction

from selectolax.parser import HTMLParser


def test_reponses_empty(app, dummy_lecture, dummy_amendements):
    from zam_repondeur.models import Lecture

    with transaction.manager:
        lecture = Lecture.get(
            chambre=dummy_lecture[0],
            session=dummy_lecture[1],
            num_texte=dummy_lecture[2],
        )
        title = str(lecture)

    resp = app.get("http://localhost/lectures/an/15/269/reponses")
    assert resp.status_code == 200
    parser = HTMLParser(resp.text)
    assert parser.tags("h1")[0].text() == title
    assert len(parser.tags("section")) == 0
    assert len(parser.tags("article")) == 0


def test_reponses_full(app, dummy_lecture, dummy_amendements):
    from zam_repondeur.models import Amendement, DBSession, Lecture

    with transaction.manager:
        lecture = Lecture.get(
            chambre=dummy_lecture[0],
            session=dummy_lecture[1],
            num_texte=dummy_lecture[2],
        )
        title = str(lecture)
        amendements = DBSession.query(Amendement).filter(
            Amendement.chambre == lecture.chambre,
            Amendement.session == lecture.session,
            Amendement.num_texte == lecture.num_texte,
        )
        for amendement in amendements.all():
            amendement.avis = "Favorable"
            amendement.observations = f"Observations pour {amendement.num}"
            amendement.reponse = f"Réponse pour {amendement.num}"
        DBSession.add_all(amendements)

    resp = app.get("http://localhost/lectures/an/15/269/reponses")
    assert resp.status_code == 200
    parser = HTMLParser(resp.text)
    assert parser.tags("h1")[0].text() == title
    assert len(parser.tags("section")) == 1
    assert len(parser.tags("article")) == 2
    assert len(parser.css("article.gouvernemental")) == 0


def test_reponses_gouvernemental(app, dummy_lecture, dummy_amendements):
    from zam_repondeur.models import Amendement, DBSession, Lecture

    with transaction.manager:
        lecture = Lecture.get(
            chambre=dummy_lecture[0],
            session=dummy_lecture[1],
            num_texte=dummy_lecture[2],
        )
        title = str(lecture)
        amendements = DBSession.query(Amendement).filter(
            Amendement.chambre == lecture.chambre,
            Amendement.session == lecture.session,
            Amendement.num_texte == lecture.num_texte,
        )
        for amendement in amendements.all():
            amendement.auteur = "LE GOUVERNEMENT"
        DBSession.add_all(amendements)

    resp = app.get("http://localhost/lectures/an/15/269/reponses")
    parser = HTMLParser(resp.text)
    assert parser.tags("h1")[0].text() == title
    assert len(parser.tags("section")) == 1
    assert len(parser.tags("article")) == 2
    assert len(parser.css("article.gouvernemental")) == 2


def test_reponses_menu(app, dummy_lecture, dummy_amendements):
    from zam_repondeur.models import Amendement, DBSession, Lecture

    with transaction.manager:
        lecture = Lecture.get(
            chambre=dummy_lecture[0],
            session=dummy_lecture[1],
            num_texte=dummy_lecture[2],
        )
        amendements = DBSession.query(Amendement).filter(
            Amendement.chambre == lecture.chambre,
            Amendement.session == lecture.session,
            Amendement.num_texte == lecture.num_texte,
        )
        for amendement in amendements.all():
            amendement.avis = "Favorable"
            amendement.observations = f"Observations pour {amendement.num}"
            amendement.reponse = f"Réponse pour {amendement.num}"
        DBSession.add_all(amendements)

    resp = app.get("http://localhost/lectures/an/15/269/reponses")
    parser = HTMLParser(resp.text)
    assert len(parser.css(".menu a")) == 1
    assert parser.css_first(".menu a").text() == "Art. 1"


def test_reponses_menu_with_textes(app, dummy_lecture, dummy_amendements):
    from zam_repondeur.models import Amendement, DBSession, Lecture

    with transaction.manager:
        lecture = Lecture.get(
            chambre=dummy_lecture[0],
            session=dummy_lecture[1],
            num_texte=dummy_lecture[2],
        )
        amendements = DBSession.query(Amendement).filter(
            Amendement.chambre == lecture.chambre,
            Amendement.session == lecture.session,
            Amendement.num_texte == lecture.num_texte,
        )
        for amendement in amendements.all():
            amendement.avis = "Favorable"
            amendement.observations = f"Observations pour {amendement.num}"
            amendement.reponse = f"Réponse pour {amendement.num}"
            amendement.subdiv_titre = "Titre article"
        DBSession.add_all(amendements)

    resp = app.get("http://localhost/lectures/an/15/269/reponses")
    parser = HTMLParser(resp.text)
    assert len(parser.css(".menu p strong")) == 1
    assert parser.css_first(".menu p strong").text() == "Titre article :"


def test_reponses_with_textes(app, dummy_lecture, dummy_amendements):
    from zam_repondeur.models import Amendement, DBSession, Lecture

    with transaction.manager:
        lecture = Lecture.get(
            chambre=dummy_lecture[0],
            session=dummy_lecture[1],
            num_texte=dummy_lecture[2],
        )
        amendements = DBSession.query(Amendement).filter(
            Amendement.chambre == lecture.chambre,
            Amendement.session == lecture.session,
            Amendement.num_texte == lecture.num_texte,
        )
        for amendement in amendements.all():
            amendement.avis = "Favorable"
            amendement.observations = f"Observations pour {amendement.num}"
            amendement.reponse = f"Réponse pour {amendement.num}"
            amendement.subdiv_titre = "Titre article"
            amendement.subdiv_contenu = {"001": "Premier paragraphe"}
        DBSession.add_all(amendements)

    resp = app.get("http://localhost/lectures/an/15/269/reponses")
    parser = HTMLParser(resp.text)
    assert len(parser.css("#content-article-1")) == 1
    assert parser.css_first("#content-article-1 dt").text() == "001"
    assert (
        parser.css_first("#content-article-1 dd").text().strip() == "Premier paragraphe"
    )


def test_reponses_without_textes(app, dummy_lecture, dummy_amendements):
    from zam_repondeur.models import Amendement, DBSession, Lecture

    with transaction.manager:
        lecture = Lecture.get(
            chambre=dummy_lecture[0],
            session=dummy_lecture[1],
            num_texte=dummy_lecture[2],
        )
        amendements = DBSession.query(Amendement).filter(
            Amendement.chambre == lecture.chambre,
            Amendement.session == lecture.session,
            Amendement.num_texte == lecture.num_texte,
        )
        for amendement in amendements.all():
            amendement.avis = "Favorable"
            amendement.observations = f"Observations pour {amendement.num}"
            amendement.reponse = f"Réponse pour {amendement.num}"
        DBSession.add_all(amendements)

    resp = app.get("http://localhost/lectures/an/15/269/reponses")
    parser = HTMLParser(resp.text)
    assert len(parser.css("#content-article-1")) == 0


def test_reponses_with_multiple_articles(app, dummy_lecture, dummy_amendements):
    from zam_repondeur.models import Amendement, DBSession, Lecture

    with transaction.manager:
        lecture = Lecture.get(
            chambre=dummy_lecture[0],
            session=dummy_lecture[1],
            num_texte=dummy_lecture[2],
        )
        amendements = DBSession.query(Amendement).filter(
            Amendement.chambre == lecture.chambre,
            Amendement.session == lecture.session,
            Amendement.num_texte == lecture.num_texte,
        )
        for index, amendement in enumerate(amendements.all(), 1):
            amendement.avis = "Favorable"
            amendement.observations = f"Observations pour {amendement.num}"
            amendement.reponse = f"Réponse pour {amendement.num}"
            amendement.subdiv_titre = f"Titre article {index}"
        # Only the last one.
        amendement.subdiv_num = 2
        DBSession.add_all(amendements)

    resp = app.get("http://localhost/lectures/an/15/269/reponses")
    parser = HTMLParser(resp.text)
    assert len(parser.tags("section")) == 2
    assert len(parser.tags("article")) == 2
    assert len(parser.css(".titles")) == 2
    for index, item in enumerate(parser.css(".titles h2"), 1):
        assert item.text() == f"Article {index}"
    for index, item in enumerate(parser.css(".titles h3"), 1):
        assert item.text() == f"Titre article {index}"
    assert len(parser.css(".menu p strong")) == 2
    for index, item in enumerate(parser.css(".menu p strong"), 1):
        assert item.text() == f"Titre article {index} :"
