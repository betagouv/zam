from pathlib import Path
import transaction

import responses

from fetch.mock_an import setup_mock_responses


HERE = Path(__file__)
SAMPLE_DATA_DIR = HERE.parent / "fetch" / "sample_data"


def read_sample_data(basename):
    return (SAMPLE_DATA_DIR / basename).read_text()


def test_get_form(app, lecture_an, amendements_an, user_david):
    resp = app.get("/dossiers/1/lectures/an.15.269.PO717460/journal/", user=user_david)

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    assert resp.forms["manual-refresh"].method == "post"
    assert (
        resp.forms["manual-refresh"].action
        == "https://zam.test/dossiers/1/lectures/an.15.269.PO717460/manual_refresh"
    )

    assert list(resp.forms["manual-refresh"].fields.keys()) == ["refresh"]

    assert resp.forms["manual-refresh"].fields["refresh"][0].attrs["type"] == "submit"


@responses.activate
def test_post_form(app, lecture_an, article1_an, user_david):
    from zam_repondeur.models import Amendement, Lecture

    # Initially, we only have one amendement (#135), with a response
    with transaction.manager:
        Amendement.create(lecture=lecture_an, article=article1_an, num=135, position=1)
        assert lecture_an.events == []

    with setup_mock_responses(
        lecture=lecture_an,
        liste=read_sample_data("an/269/liste.xml"),
        amendements=(
            ("177", read_sample_data("an/269/177.xml")),
            ("270", read_sample_data("an/269/270.xml")),
            ("723", read_sample_data("an/269/723.xml")),
            ("135", read_sample_data("an/269/135.xml")),
            ("192", read_sample_data("an/269/192.xml")),
        ),
    ) as mock_resp:

        mock_resp.add(
            responses.GET,
            "http://www.assemblee-nationale.fr/15/projets/pl0269.asp",
            body=(Path(__file__).parent / "sample_data" / "pl0269.html").read_text(
                "utf-8", "ignore"
            ),
            status=200,
        )

        # Then we ask for a refresh
        form = app.get(
            "/dossiers/1/lectures/an.15.269.PO717460/journal/", user=user_david
        ).forms["manual-refresh"]
        resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == f"https://zam.test/{lecture_an.url}"

    resp = resp.follow()

    assert resp.status_code == 200

    lecture_an = Lecture.get_by_pk(lecture_an.pk)  # refresh object

    events = lecture_an.events
    assert len(events) == 2
    assert events[0].render_summary() == "Le contenu des articles a été récupéré."
    assert events[1].render_summary() == "4 nouveaux amendements récupérés."
    assert "Rafraichissement des amendements et des articles en cours." in resp.text
