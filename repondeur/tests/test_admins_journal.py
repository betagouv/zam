import transaction
from pyramid.testing import DummyRequest


def first_description_text(resp):
    return resp.parser.css_first(".timeline li .what").text().strip()


def test_admin_set(app, user_sgg, user_david):
    from zam_repondeur.models.events.admin import AdminSet

    with transaction.manager:
        AdminSet.create(
            target=user_david,
            request=DummyRequest(remote_addr="127.0.0.1", user=user_sgg),
        )

    resp = app.get("/admins/journal", user=user_sgg)
    assert first_description_text(resp) == (
        "SGG user a ajouté David (david@exemple.gouv.fr) "
        "à la liste des administrateur·ice·s."
    )


def test_admin_unset(app, user_sgg, user_david):
    from zam_repondeur.models.events.admin import AdminUnset

    with transaction.manager:
        AdminUnset.create(
            target=user_david,
            request=DummyRequest(remote_addr="127.0.0.1", user=user_sgg),
        )

    resp = app.get("/admins/journal", user=user_sgg)
    assert first_description_text(resp) == (
        "SGG user a retiré David (david@exemple.gouv.fr) "
        "de la liste des administrateur·ice·s."
    )
