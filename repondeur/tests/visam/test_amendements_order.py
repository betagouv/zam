import pytest


@pytest.mark.usefixtures("amendement_222_lecture_seance_ccfp")
def test_lecture_reorder_amendements_unique_amendement(
    app, seance_ccfp, lecture_seance_ccfp, user_ccfp
):
    lecture = lecture_seance_ccfp
    dossier = lecture.dossier
    resp = app.get(
        f"/seances/{seance_ccfp.slug}/textes/{dossier.slug}/amendements/",
        user=user_ccfp,
    )
    assert resp.status_code == 200
    assert (
        '<script src="https://visam.test/static/js/amendements-order.js'
        not in resp.text
    )


def test_lecture_reorder_amendements_many_amendements(
    app,
    seance_ccfp,
    lecture_seance_ccfp,
    amendement_222_lecture_seance_ccfp,
    amendement_444_lecture_seance_ccfp,
    user_ccfp,
):
    from zam_repondeur.models import Amendement

    lecture = lecture_seance_ccfp
    dossier = lecture.dossier

    # Initial positions
    assert amendement_222_lecture_seance_ccfp.position == 1
    assert amendement_444_lecture_seance_ccfp.position == 2

    resp = app.get(
        f"/seances/{seance_ccfp.slug}/textes/{dossier.slug}/amendements/",
        user=user_ccfp,
    )
    assert resp.status_code == 200
    assert '<script src="https://visam.test/static/js/amendements-order.js' in resp.text

    resp = app.post_json(
        f"/seances/{seance_ccfp.slug}/textes/{dossier.slug}/amendements/order",
        {"order": ["v444", "v222"]},
        user=user_ccfp,
    )
    assert resp.status_code == 200
    assert resp.text == "{}"

    # Positions have changed
    amendement_222_lecture_seance_ccfp = Amendement.get(
        lecture, amendement_222_lecture_seance_ccfp.num
    )
    amendement_444_lecture_seance_ccfp = Amendement.get(
        lecture, amendement_444_lecture_seance_ccfp.num
    )
    assert amendement_222_lecture_seance_ccfp.position == 2
    assert amendement_444_lecture_seance_ccfp.position == 1
