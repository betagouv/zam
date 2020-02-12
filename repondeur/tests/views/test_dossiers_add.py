import json
import re
from pathlib import Path

import responses
import transaction
from webtest.forms import Select

HERE = Path(__file__)
SAMPLE_DATA_DIR = HERE.parent.parent / "sample_data"
FETCH_SAMPLE_DATA_DIR = HERE.parent.parent / "fetch" / "sample_data"


def read_sample_data(basename):
    return (FETCH_SAMPLE_DATA_DIR / basename).read_text()


def read_sample_data_bytes(basename):
    return (FETCH_SAMPLE_DATA_DIR / basename).read_bytes()


def test_get_form(app, user_sgg, dossier_plfss2018):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        dossier_plfss2018.team = None
        DBSession.add(dossier_plfss2018)

    resp = app.get("/dossiers/add", user=user_sgg)

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


def test_get_form_non_sgg_user(app, user_david):
    resp = app.get("/dossiers/add", user=user_david)

    assert resp.status_code == 302
    assert resp.location == "https://zam.test/"

    resp = resp.maybe_follow()

    assert resp.status_code == 200
    assert "L’accès à ce dossier est réservé aux personnes autorisées." in resp.text


def test_get_form_does_not_propose_dossiers_with_teams(
    app, user_sgg, dossier_plfss2018
):
    resp = app.get("/dossiers/add", user=user_sgg)
    form = resp.forms["add-dossier"]
    assert form.fields["dossier"][0].options == [("", True, "")]


class TestPostForm:
    @responses.activate
    def test_plfss_2018_an(self, app, user_sgg, dossier_plfss2018):
        from zam_repondeur.models import Chambre, DBSession, Dossier, Lecture, User

        with transaction.manager:
            DBSession.add(user_sgg)
            assert len(user_sgg.teams) == 0

        assert not DBSession.query(Lecture).all()

        responses.add(
            responses.GET,
            "http://www.assemblee-nationale.fr/eloi/15/amendements/0269/AN/liste.xml",
            body=read_sample_data("an/269/liste.xml"),
            status=200,
        )
        responses.add(
            responses.GET,
            "http://www.assemblee-nationale.fr/dyn/15/amendements/0269/AN/177.xml",
            body=read_sample_data("an/269/177.xml"),
            status=200,
        )
        responses.add(
            responses.GET,
            "http://www.assemblee-nationale.fr/dyn/15/amendements/0269/AN/270.xml",
            body=read_sample_data("an/269/270.xml"),
            status=200,
        )
        responses.add(
            responses.GET,
            "http://www.assemblee-nationale.fr/dyn/15/amendements/0269/AN/723.xml",
            body=read_sample_data("an/269/723.xml"),
            status=200,
        )
        responses.add(
            responses.GET,
            "http://www.assemblee-nationale.fr/dyn/15/amendements/0269/AN/135.xml",
            body=read_sample_data("an/269/135.xml"),
            status=200,
        )
        responses.add(
            responses.GET,
            "http://www.assemblee-nationale.fr/dyn/15/amendements/0269/AN/192.xml",
            body=read_sample_data("an/269/192.xml"),
            status=200,
        )
        responses.add(
            responses.GET,
            "http://www.assemblee-nationale.fr/15/projets/pl0269.asp",
            body=(SAMPLE_DATA_DIR / "pl0269.html").read_text("utf-8", "ignore"),
            status=200,
        )

        responses.add(
            responses.GET,
            "https://www.senat.fr/leg/pjl17-063.html",
            body=(SAMPLE_DATA_DIR / "pjl17-063.html").read_text("utf-8", "ignore"),
            status=200,
        )
        responses.add(
            responses.GET,
            (
                "https://www.senat.fr"
                "/amendements/2017-2018/63/jeu_complet_2017-2018_63.csv"
            ),
            body=read_sample_data_bytes("senat/jeu_complet_2017-2018_63.csv"),
            status=200,
        )
        responses.add(
            responses.GET,
            "https://www.senat.fr/enseance/2017-2018/63/liste_discussion.json",
            json=json.loads(read_sample_data_bytes("senat/liste_discussion_63.json")),
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
            body=(FETCH_SAMPLE_DATA_DIR / "senat" / "ODSEN_GENERAL.csv").read_bytes(),
            status=200,
        )
        responses.add(
            responses.GET,
            "https://www.senat.fr/dossier-legislatif/rss/doslegplfss2018.xml",
            body=(SAMPLE_DATA_DIR / "doslegplfss2018.xml").read_bytes(),
            status=200,
        )

        with transaction.manager:
            dossier_plfss2018.team = None
            DBSession.add(dossier_plfss2018)

        resp = app.get("/dossiers/add", user=user_sgg)
        form = resp.forms["add-dossier"]
        form["dossier"] = "plfss-2018"
        resp = form.submit()

        assert resp.status_code == 302
        assert resp.location == "https://zam.test/dossiers/plfss-2018/"

        resp = resp.follow()

        assert resp.status_code == 200
        assert "Dossier créé avec succès," in resp.text

        user_sgg = DBSession.query(User).filter(User.pk == user_sgg.pk).one()
        dossier_plfss2018 = (
            DBSession.query(Dossier).filter(Dossier.slug == "plfss-2018").one()
        )
        assert len(user_sgg.teams) == 1
        assert dossier_plfss2018.team in user_sgg.teams
        assert len(dossier_plfss2018.events) == 2
        assert (
            dossier_plfss2018.events[0].render_summary()
            == "<abbr title='user@sgg.pm.gouv.fr'>SGG user</abbr> a activé le dossier."
        )
        assert (
            dossier_plfss2018.events[1].render_summary()
            == "De nouvelles lectures ont été récupérées."
        )

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
            == "<abbr title='user@sgg.pm.gouv.fr'>SGG user</abbr> a créé la lecture."
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
        assert [amdt.num for amdt in lecture.amendements] == [177, 270, 723, 192, 135]

    @responses.activate
    def test_plfss_2018_an_using_fallback(self, app, user_sgg, dossier_plfss2018):
        from zam_repondeur.models import Chambre, DBSession, Dossier, Lecture, User

        with transaction.manager:
            DBSession.add(user_sgg)
            assert len(user_sgg.teams) == 0

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
                r"http://www\.assemblee-nationale\.fr/dyn/15/amendements/0269/AN/\d+\.xml"  # noqa
            ),
            status=404,
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
            body=(SAMPLE_DATA_DIR / "pl0269.html").read_text("utf-8", "ignore"),
            status=200,
        )

        responses.add(
            responses.GET,
            "https://www.senat.fr/dossier-legislatif/rss/doslegplfss2018.xml",
            body=(SAMPLE_DATA_DIR / "doslegplfss2018.xml").read_bytes(),
            status=200,
        )
        responses.add(
            responses.GET,
            "https://www.senat.fr/leg/pjl17-063.html",
            body=(SAMPLE_DATA_DIR / "pjl17-063.html").read_text("utf-8", "ignore"),
            status=200,
        )
        responses.add(
            responses.GET,
            (
                "https://www.senat.fr"
                "/amendements/2017-2018/63/jeu_complet_2017-2018_63.csv"
            ),
            body=read_sample_data_bytes("senat/jeu_complet_2017-2018_63.csv"),
            status=200,
        )
        responses.add(
            responses.GET,
            "https://www.senat.fr/enseance/2017-2018/63/liste_discussion.json",
            json=json.loads(read_sample_data_bytes("senat/liste_discussion_63.json")),
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
            body=(FETCH_SAMPLE_DATA_DIR / "senat" / "ODSEN_GENERAL.csv").read_bytes(),
            status=200,
        )

        with transaction.manager:
            dossier_plfss2018.team = None
            DBSession.add(dossier_plfss2018)

        resp = app.get("/dossiers/add", user=user_sgg)
        form = resp.forms["add-dossier"]
        form["dossier"] = "plfss-2018"
        resp = form.submit()

        assert resp.status_code == 302
        assert resp.location == "https://zam.test/dossiers/plfss-2018/"

        resp = resp.follow()

        assert resp.status_code == 200
        assert "Dossier créé avec succès," in resp.text

        user_sgg = DBSession.query(User).filter(User.pk == user_sgg.pk).one()
        dossier_plfss2018 = (
            DBSession.query(Dossier).filter(Dossier.slug == "plfss-2018").one()
        )
        assert len(user_sgg.teams) == 1
        assert dossier_plfss2018.team in user_sgg.teams
        assert len(dossier_plfss2018.events) == 2
        assert (
            dossier_plfss2018.events[0].render_summary()
            == "<abbr title='user@sgg.pm.gouv.fr'>SGG user</abbr> a activé le dossier."
        )
        assert (
            dossier_plfss2018.events[1].render_summary()
            == "De nouvelles lectures ont été récupérées."
        )

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
            == "<abbr title='user@sgg.pm.gouv.fr'>SGG user</abbr> a créé la lecture."
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
        assert [amdt.num for amdt in lecture.amendements] == [177, 270, 723, 192, 135]

    @responses.activate
    def test_plfss_2019_senat(self, app, user_sgg, dossier_plfss2019):
        from zam_repondeur.models import Chambre, DBSession, Lecture

        assert not DBSession.query(Lecture).all()

        responses.add(
            responses.GET,
            "https://www.senat.fr/amendements/2018-2019/106/jeu_complet_2018-2019_106.csv",  # noqa
            body=(
                FETCH_SAMPLE_DATA_DIR / "senat" / "jeu_complet_2018-2019_106.csv"
            ).read_bytes(),
            status=200,
        )
        responses.add(
            responses.GET,
            "https://www.senat.fr/enseance/2018-2019/106/liste_discussion.json",
            body=(
                FETCH_SAMPLE_DATA_DIR / "senat" / "liste_discussion_106.json"
            ).read_bytes(),
            status=200,
        )
        responses.add(
            responses.GET,
            "https://www.senat.fr/dossier-legislatif/rss/doslegplfss2019.xml",
            body=(SAMPLE_DATA_DIR / "doslegplfss2019.xml").read_bytes(),
            status=200,
        )
        responses.add(
            responses.GET,
            "https://www.senat.fr/leg/pjl18-106.html",
            body=(SAMPLE_DATA_DIR / "pjl18-106.html").read_text("utf-8", "ignore"),
            status=200,
        )
        responses.add(
            responses.GET,
            "https://data.senat.fr/data/senateurs/ODSEN_GENERAL.csv",
            body=(FETCH_SAMPLE_DATA_DIR / "senat" / "ODSEN_GENERAL.csv").read_bytes(),
            status=200,
        )

        resp = app.get("/dossiers/add", user=user_sgg)
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
        assert lecture.titre == "Première lecture – Séance publique"
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
            == "<abbr title='user@sgg.pm.gouv.fr'>SGG user</abbr> a créé la lecture."
        )

        # We should have articles from the page (1) and from the amendements (19, 29)
        assert {article.num for article in lecture.articles} == {"1", "19", "29"}

        # We should have loaded 2 amendements
        assert [amdt.num for amdt in lecture.amendements] == [629, 1]

    @responses.activate
    def test_plfss_2018_an_dossier_already_activated(
        self, app, dossier_plfss2018, lecture_an, user_sgg
    ):
        from zam_repondeur.models import DBSession

        # We cannot use form.submit() given the form does not contain that choice.
        resp = app.post("/dossiers/add", {"dossier": "plfss-2018"}, user=user_sgg)

        assert resp.status_code == 302
        assert resp.location == "https://zam.test/dossiers/"

        resp = resp.follow()

        assert resp.status_code == 200
        assert "Ce dossier appartient à une autre équipe…" in resp.text

        DBSession.add(lecture_an)
        assert len(lecture_an.events) == 0

    @responses.activate
    def test_plfss_2018_an_dossier_unknown(
        self, app, dossier_plfss2018, lecture_an, user_sgg
    ):
        from zam_repondeur.models import DBSession

        # We cannot use form.submit() given the form does not contain that choice.
        resp = app.post("/dossiers/add", {"dossier": "plfss-2019"}, user=user_sgg)

        assert resp.status_code == 302
        assert resp.location == "https://zam.test/dossiers/"

        resp = resp.follow()

        assert resp.status_code == 200
        assert "Ce dossier n’existe pas." in resp.text

        DBSession.add(lecture_an)
        assert len(lecture_an.events) == 0

    @responses.activate
    def test_plfss_2018_an_dossier_empty(
        self, app, dossier_plfss2018, lecture_an, user_sgg
    ):
        from zam_repondeur.models import DBSession

        # We cannot use form.submit() given the form does not contain that choice.
        resp = app.post("/dossiers/add", {"dossier": ""}, user=user_sgg)

        assert resp.status_code == 302
        assert resp.location == "https://zam.test/dossiers/"

        resp = resp.follow()

        assert resp.status_code == 200
        assert "Ce dossier n’existe pas." in resp.text

        DBSession.add(lecture_an)
        assert len(lecture_an.events) == 0
