import transaction
from pyramid.testing import DummyRequest


def first_description_text(resp):
    return resp.parser.css_first(".timeline li .what").text().strip()


def test_admin_grant(app, user_sgg, user_david):
    from zam_repondeur.models.events.admin import AdminGrant

    with transaction.manager:
        AdminGrant.create(
            target=user_david,
            request=DummyRequest(remote_addr="127.0.0.1", user=user_sgg),
        )

    resp = app.get("/admins/journal", user=user_sgg)
    assert first_description_text(resp) == (
        "SGG user a ajouté David (david@exemple.gouv.fr) "
        "à la liste des administrateur·ice·s."
    )


def test_admin_revoke(app, user_sgg, user_david):
    from zam_repondeur.models.events.admin import AdminRevoke

    with transaction.manager:
        AdminRevoke.create(
            target=user_david,
            request=DummyRequest(remote_addr="127.0.0.1", user=user_sgg),
        )

    resp = app.get("/admins/journal", user=user_sgg)
    assert first_description_text(resp) == (
        "SGG user a retiré David (david@exemple.gouv.fr) "
        "de la liste des administrateur·ice·s."
    )
