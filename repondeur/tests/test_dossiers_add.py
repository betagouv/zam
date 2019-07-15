import json
import re
from datetime import datetime
from pathlib import Path

import responses
import transaction
from webtest.forms import Select

HERE = Path(__file__)
SAMPLE_DATA_DIR = HERE.parent / "fetch" / "sample_data"


def read_sample_data(basename):
    return (SAMPLE_DATA_DIR / basename).read_text()


def test_get_form(app, user_david, dossier_plfss2018):
    resp = app.get("/dossiers/add", user=user_david)

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    # Check the form
    form = resp.forms["add-dossier"]
    assert form.method == "POST"
    assert form.action == "/dossiers/add"

    assert list(form.fields.keys()) == ["dossier", "submit"]

    assert isinstance(form.fields["dossier"][0], Select)
    assert form.fields["dossier"][0].options == [
        ("", True, ""),
        ("plfss-2018", False, "Sécurité sociale : loi de financement 2018"),
    ]

    assert form.fields["submit"][0].attrs["type"] == "submit"


def test_get_form_does_not_propose_activated_choices(
    app, user_david, dossier_plfss2018, lecture_an
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        lecture_an.dossier.activated_at = datetime.utcnow()
        DBSession.add(lecture_an)

    resp = app.get("/dossiers/add", user=user_david)
    form = resp.forms["add-dossier"]
    assert form.fields["dossier"][0].options == [("", True, "")]


class TestPostForm:
    @responses.activate
    def test_plfss_2018_an(self, app, user_david, dossier_plfss2018):
        from zam_repondeur.models import Chambre, DBSession, Dossier, Lecture

        with transaction.manager:
            DBSession.add(user_david)

        assert not DBSession.query(Dossier).all()
        assert not DBSession.query(Lecture).all()

        responses.add(
            responses.GET,
            "http://www.assemblee-nationale.fr/eloi/15/amendements/0269/AN/liste.xml",
            body=read_sample_data("an/269/liste.xml"),
            status=200,
        )
        responses.add(
            responses.GET,
            "http://www.assemblee-nationale.fr/15/xml/amendements/0269/AN/177.xml",
            body=read_sample_data("an/269/177.xml"),
            status=200,
        )
        responses.add(
            responses.GET,
            "http://www.assemblee-nationale.fr/15/xml/amendements/0269/AN/270.xml",
            body=read_sample_data("an/269/270.xml"),
            status=200,
        )
        responses.add(
            responses.GET,
            "http://www.assemblee-nationale.fr/15/xml/amendements/0269/AN/723.xml",
            body=read_sample_data("an/269/723.xml"),
            status=200,
        )
        responses.add(
            responses.GET,
            "http://www.assemblee-nationale.fr/15/xml/amendements/0269/AN/135.xml",
            body=read_sample_data("an/269/135.xml"),
            status=200,
        )
        responses.add(
            responses.GET,
            "http://www.assemblee-nationale.fr/15/xml/amendements/0269/AN/192.xml",
            body=read_sample_data("an/269/192.xml"),
            status=200,
        )
        responses.add(
            responses.GET,
            re.compile(
                r"http://www\.assemblee-nationale\.fr/15/xml/amendements/0269/AN/\d+\.xml"  # noqa
            ),
            status=404,
        )
        responses.add(
            responses.GET,
            "http://www.assemblee-nationale.fr/15/projets/pl0269.asp",
            body=(HERE.parent / "sample_data" / "pl0269.html").read_text(
                "utf-8", "ignore"
            ),
            status=200,
        )

        responses.add(
            responses.GET,
            "https://www.senat.fr/leg/pjl17-063.html",
            body=(HERE.parent / "sample_data" / "pjl17-063.html").read_text(
                "utf-8", "ignore"
            ),
            status=200,
        )
        responses.add(
            responses.GET,
            (
                "https://www.senat.fr"
                "/amendements/2017-2018/63/jeu_complet_2017-2018_63.csv"
            ),
            body=(
                HERE.parent
                / "fetch"
                / "sample_data"
                / "senat"
                / "jeu_complet_2017-2018_63.csv"
            ).read_bytes(),
            status=200,
        )
        responses.add(
            responses.GET,
            "https://www.senat.fr/enseance/2017-2018/63/liste_discussion.json",
            json=json.loads(
                (
                    HERE.parent
                    / "fetch"
                    / "sample_data"
                    / "senat"
                    / "liste_discussion_63.json"
                ).read_bytes()
            ),
            status=200,
        )
        responses.add(
            responses.GET,
            "https://www.senat.fr/encommission/2017-2018/63/liste_discussion.json",
            status=404,
        )
        responses.add(
            responses.GET,
            "https://data.senat.fr/data/senateurs/ODSEN_GENERAL.csv",
            body=(
                HERE.parent / "fetch" / "sample_data" / "senat" / "ODSEN_GENERAL.csv"
            ).read_bytes(),
            status=200,
        )

        resp = app.get("/dossiers/add", user=user_david)
        form = resp.forms["add-dossier"]
        form["dossier"] = "plfss-2018"
        resp = form.submit()

        assert resp.status_code == 302
        assert resp.location == "https://zam.test/dossiers/plfss-2018/"

        resp = resp.follow()

        assert resp.status_code == 200
        assert "Dossier créé avec succès," in resp.text
        lecture = Lecture.get(
            chambre=Chambre.AN,
            session_or_legislature="15",
            num_texte=269,
            partie=None,
            organe="PO717460",
        )

        assert lecture.chambre == Chambre.AN
        assert lecture.titre == "Première lecture – Titre lecture"
        assert lecture.dossier.titre == "Sécurité sociale : loi de financement 2018"
        result = (
            "Assemblée nationale, 15e législature, Séance publique, Première lecture, "
            "texte nº\u00a0269"
        )
        assert str(lecture) == result

        # We should have an event entry for articles, and one for amendements
        assert len(lecture.events) == 3
        assert lecture.events[0].render_summary() == "5 nouveaux amendements récupérés."
        assert (
            lecture.events[1].render_summary()
            == "Le contenu des articles a été récupéré."
        )
        assert (
            lecture.events[2].render_summary()
            == "<abbr title='david@exemple.gouv.fr'>David</abbr> a créé la lecture."
        )

        # We expect articles from the page (1, 2) and from the amendements (3, 8, 9)
        assert {article.num for article in lecture.articles} == {
            "1",
            "2",
            "3",
            "8",
            "9",
        }

        # We should have loaded 5 amendements
        assert [amdt.num for amdt in lecture.amendements] == [177, 270, 723, 135, 192]

    @responses.activate
    def test_plfss_2019_senat(self, app, user_david, dossier_plfss2019):
        from zam_repondeur.models import Chambre, DBSession, Dossier, Lecture

        with transaction.manager:
            DBSession.add(user_david)

        assert not DBSession.query(Dossier).all()
        assert not DBSession.query(Lecture).all()

        responses.add(
            responses.GET,
            "https://www.senat.fr/amendements/2018-2019/106/jeu_complet_2018-2019_106.csv",  # noqa
            body=(
                HERE.parent
                / "fetch"
                / "sample_data"
                / "senat"
                / "jeu_complet_2018-2019_106.csv"
            ).read_bytes(),
            status=200,
        )
        responses.add(
            responses.GET,
            "https://www.senat.fr/enseance/2018-2019/106/liste_discussion.json",
            body=(
                HERE.parent
                / "fetch"
                / "sample_data"
                / "senat"
                / "liste_discussion_106.json"
            ).read_bytes(),
            status=200,
        )
        responses.add(
            responses.GET,
            "https://www.senat.fr/leg/pjl18-106.html",
            body=(HERE.parent / "sample_data" / "pjl18-106.html").read_text(
                "utf-8", "ignore"
            ),
            status=200,
        )
        responses.add(
            responses.GET,
            "https://data.senat.fr/data/senateurs/ODSEN_GENERAL.csv",
            body=(
                HERE.parent / "fetch" / "sample_data" / "senat" / "ODSEN_GENERAL.csv"
            ).read_bytes(),
            status=200,
        )

        resp = app.get("/dossiers/add", user=user_david)
        form = resp.forms["add-dossier"]
        form["dossier"] = "plfss-2019"
        resp = form.submit()

        assert resp.status_code == 302
        assert resp.location == "https://zam.test/dossiers/plfss-2019/"

        resp = resp.follow()

        assert resp.status_code == 200
        assert "Dossier créé avec succès," in resp.text

        lecture = Lecture.get(
            chambre=Chambre.SENAT,
            session_or_legislature="2018-2019",
            num_texte=106,
            partie=None,
            organe="PO78718",
        )
        assert lecture.chambre == Chambre.SENAT
        assert lecture.titre == "Première lecture – Titre lecture"
        assert lecture.dossier.titre == "Sécurité sociale : loi de financement 2019"
        result = (
            "Sénat, session 2018-2019, Séance publique, Première lecture, texte nº 106"
        )
        assert str(lecture) == result

        # We should have an event entry for articles, and one for amendements
        assert len(lecture.events) == 3
        assert lecture.events[0].render_summary() == "2 nouveaux amendements récupérés."
        assert (
            lecture.events[1].render_summary()
            == "Le contenu des articles a été récupéré."
        )
        assert (
            lecture.events[2].render_summary()
            == "<abbr title='david@exemple.gouv.fr'>David</abbr> a créé la lecture."
        )

        # We should have articles from the page (1) and from the amendements (19, 29)
        assert {article.num for article in lecture.articles} == {"1", "19", "29"}

        # We should have loaded 2 amendements
        assert [amdt.num for amdt in lecture.amendements] == [629, 1]

    @responses.activate
    def test_plfss_2018_an_dossier_already_activated(
        self, app, dossier_plfss2018, lecture_an, user_david
    ):
        from zam_repondeur.models import DBSession

        with transaction.manager:
            lecture_an.dossier.activated_at = datetime.utcnow()
            DBSession.add(lecture_an)

        # We cannot use form.submit() given the form does not contain that choice.
        resp = app.post("/dossiers/add", {"dossier": "plfss-2018"}, user=user_david)

        assert resp.status_code == 302
        assert resp.location == "https://zam.test/dossiers/"

        resp = resp.follow()

        assert resp.status_code == 200
        assert "Ce dossier appartient à une autre équipe…" in resp.text

        DBSession.add(lecture_an)
        assert len(lecture_an.events) == 0

    @responses.activate
    def test_plfss_2018_an_dossier_unknown(
        self, app, dossier_plfss2018, lecture_an, user_david
    ):
        from zam_repondeur.models import DBSession

        with transaction.manager:
            lecture_an.dossier.activated_at = datetime.utcnow()
            DBSession.add(lecture_an)

        # We cannot use form.submit() given the form does not contain that choice.
        resp = app.post("/dossiers/add", {"dossier": "plfss-2019"}, user=user_david)

        assert resp.status_code == 302
        assert resp.location == "https://zam.test/dossiers/"

        resp = resp.follow()

        assert resp.status_code == 200
        assert "Ce dossier n’existe pas." in resp.text

        DBSession.add(lecture_an)
        assert len(lecture_an.events) == 0

    @responses.activate
    def test_plfss_2018_an_dossier_empty(
        self, app, dossier_plfss2018, lecture_an, user_david
    ):
        from zam_repondeur.models import DBSession

        with transaction.manager:
            lecture_an.dossier.activated_at = datetime.utcnow()
            DBSession.add(lecture_an)

        # We cannot use form.submit() given the form does not contain that choice.
        resp = app.post("/dossiers/add", {"dossier": ""}, user=user_david)

        assert resp.status_code == 302
        assert resp.location == "https://zam.test/dossiers/"

        resp = resp.follow()

        assert resp.status_code == 200
        assert "Ce dossier n’existe pas." in resp.text

        DBSession.add(lecture_an)
        assert len(lecture_an.events) == 0
