import transaction
from pyramid.testing import DummyRequest


def first_description_text(resp):
    return resp.parser.css_first(".timeline li .what").text().strip()


def test_whitelist_add(app, user_sgg, user_david):
    from zam_repondeur.models.events.whitelist import WhitelistAdd

    with transaction.manager:
        WhitelistAdd.create(
            email_pattern="foo@bar.gouv.fr",
            comment=None,
            request=DummyRequest(remote_addr="127.0.0.1", user=user_sgg),
        )

    resp = app.get("/whitelist/journal", user=user_sgg)
    assert first_description_text(resp) == (
        "SGG user a ajouté foo@bar.gouv.fr à la liste blanche."
    )


def test_whitelist_remove(app, user_sgg, whitelist):
    from zam_repondeur.models.events.whitelist import WhitelistRemove

    with transaction.manager:
        WhitelistRemove.create(
            allowed_email_pattern=whitelist,
            request=DummyRequest(remote_addr="127.0.0.1", user=user_sgg),
        )

    resp = app.get("/whitelist/journal", user=user_sgg)
    assert first_description_text(resp) == (
        "SGG user a retiré *@*.gouv.fr de la liste blanche."
    )
