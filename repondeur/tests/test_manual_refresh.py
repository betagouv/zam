from pathlib import Path
import transaction

import responses

from zam_repondeur.fetch.an.amendements import build_url

HERE = Path(__file__)
SAMPLE_DATA_DIR = HERE.parent / "fetch" / "sample_data"


def read_sample_data(basename):
    return (SAMPLE_DATA_DIR / basename).read_text()


def test_get_form(app, lecture_an, amendements_an):
    resp = app.get("/lectures/an.15.269.PO717460/journal/")

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    assert resp.forms["manual-refresh"].method == "post"
    assert (
        resp.forms["manual-refresh"].action
        == "http://localhost/lectures/an.15.269.PO717460/manual_refresh"
    )

    assert list(resp.forms["manual-refresh"].fields.keys()) == ["refresh"]

    assert resp.forms["manual-refresh"].fields["refresh"][0].attrs["type"] == "submit"


@responses.activate
def test_post_form(app, lecture_an, article1_an):
    from zam_repondeur.models import DBSession, Amendement, Lecture

    initial_modified_at = lecture_an.modified_at

    responses.add(
        responses.GET,
        build_url(15, 269),
        body=read_sample_data("an/269/liste.xml"),
        status=200,
    )
    responses.add(
        responses.GET,
        build_url(15, 269, 177),
        body=read_sample_data("an/269/177.xml"),
        status=200,
    )
    responses.add(
        responses.GET,
        build_url(15, 269, 270),
        body=read_sample_data("an/269/270.xml"),
        status=200,
    )
    responses.add(
        responses.GET,
        build_url(15, 269, 723),
        body=read_sample_data("an/269/723.xml"),
        status=200,
    )
    responses.add(
        responses.GET,
        build_url(15, 269, 135),
        body=read_sample_data("an/269/135.xml"),
        status=200,
    )
    responses.add(
        responses.GET,
        build_url(15, 269, 192),
        body=read_sample_data("an/269/192.xml"),
        status=200,
    )

    responses.add(
        responses.GET,
        "http://www.assemblee-nationale.fr/15/projets/pl0269.asp",
        body=(Path(__file__).parent / "sample_data" / "pl0269.html").read_text(
            "utf-8", "ignore"
        ),
        status=200,
    )

    # Initially, we only have one amendement (#135), with a response
    with transaction.manager:
        amendement = Amendement(
            lecture=lecture_an, article=article1_an, num=135, position=1
        )
        DBSession.add(amendement)

    # Then we ask for a refresh
    form = app.get("/lectures/an.15.269.PO717460/journal/").forms["manual-refresh"]
    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == "http://localhost/lectures/an.15.269.PO717460/journal"

    resp = resp.follow()

    assert resp.status_code == 200
    assert "4 nouveaux amendements récupérés." in resp.text

    # Check that the update timestamp has been updated
    with transaction.manager:
        lecture = Lecture.get(
            chambre=lecture_an.chambre,
            session=lecture_an.session,
            num_texte=lecture_an.num_texte,
            organe=lecture_an.organe,
        )
        assert lecture.modified_at != initial_modified_at
