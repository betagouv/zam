from urllib.parse import quote

import pytest


@pytest.mark.usefixtures("amendement_222_lecture_conseil_ccfp")
def test_lecture_reorder_amendements_unique_amendement(
    app, lecture_conseil_ccfp, user_david
):
    lecture = lecture_conseil_ccfp
    dossier = lecture.dossier
    resp = app.get(
        f"/dossiers/{dossier.slug}/lectures/{quote(lecture.url_key)}/amendements/",
        user=user_david,
    )
    assert resp.status_code == 200
    assert (
        '<script src="https://visam.test/static/js/amendements-order.js'
        not in resp.text
    )


def test_lecture_reorder_amendements_many_amendements(
    app,
    lecture_conseil_ccfp,
    amendement_222_lecture_conseil_ccfp,
    amendement_444_lecture_conseil_ccfp,
    user_david,
):
    from zam_repondeur.models import Amendement

    lecture = lecture_conseil_ccfp
    dossier = lecture.dossier

    # Initial positions
    assert amendement_222_lecture_conseil_ccfp.position == 1
    assert amendement_444_lecture_conseil_ccfp.position == 2

    resp = app.get(
        f"/dossiers/{dossier.slug}/lectures/{quote(lecture.url_key)}/amendements/",
        user=user_david,
    )
    assert resp.status_code == 200
    assert '<script src="https://visam.test/static/js/amendements-order.js' in resp.text

    resp = app.post_json(
        f"/dossiers/{dossier.slug}/lectures/{quote(lecture.url_key)}/amendements/order",
        {"order": ["v444", "v222"]},
        user=user_david,
    )
    assert resp.status_code == 200
    assert resp.text == "{}"

    # Positions have changed
    amendement_222_lecture_conseil_ccfp = Amendement.get(
        lecture, amendement_222_lecture_conseil_ccfp.num
    )
    amendement_444_lecture_conseil_ccfp = Amendement.get(
        lecture, amendement_444_lecture_conseil_ccfp.num
    )
    assert amendement_222_lecture_conseil_ccfp.position == 2
    assert amendement_444_lecture_conseil_ccfp.position == 1
