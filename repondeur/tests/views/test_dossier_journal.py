import transaction
from pyramid.testing import DummyRequest


def first_description_text(resp):
    return resp.parser.css_first(".timeline li .what").text().strip()


def test_dossier_activation(app, dossier_plfss2018, user_david):
    from zam_repondeur.models.events.dossier import DossierActive

    with transaction.manager:
        DossierActive.create(
            dossier=dossier_plfss2018,
            request=DummyRequest(remote_addr="127.0.0.1", user=user_david),
        )
        assert len(dossier_plfss2018.events) == 1

    resp = app.get("/dossiers/plfss-2018/journal", user=user_david)
    assert first_description_text(resp) == "David a activé le dossier."


def test_dossier_lectures_recuperation(app, dossier_plfss2018, user_david):
    from zam_repondeur.models.events.dossier import LecturesRecuperees

    with transaction.manager:
        LecturesRecuperees.create(dossier=dossier_plfss2018, user=user_david)
        assert len(dossier_plfss2018.events) == 1

    resp = app.get("/dossiers/plfss-2018/journal", user=user_david)
    assert first_description_text(resp) == "De nouvelles lectures ont été récupérées."


def test_dossier_invitation_envoyee(app, dossier_plfss2018, user_david):
    from zam_repondeur.models.events.dossier import InvitationEnvoyee

    with transaction.manager:
        InvitationEnvoyee.create(
            dossier=dossier_plfss2018,
            email="foo@exemple.gouv.fr",
            request=DummyRequest(remote_addr="127.0.0.1", user=user_david),
        )
        assert len(dossier_plfss2018.events) == 1

    resp = app.get("/dossiers/plfss-2018/journal", user=user_david)
    assert first_description_text(resp) == "David a invité « foo@exemple.gouv.fr »"
