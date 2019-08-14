import transaction


def first_description_text(resp):
    return resp.parser.css_first(".timeline li .what").text().strip()


def test_dossier_activation(app, dossier_plfss2018, user_david):
    from zam_repondeur.models.events.dossier import DossierActive

    with transaction.manager:
        DossierActive.create(request=None, dossier=dossier_plfss2018, user=user_david)
        assert len(dossier_plfss2018.events) == 1

    resp = app.get("/dossiers/plfss-2018/journal", user=user_david)
    assert first_description_text(resp) == "David a activé le dossier."


def test_dossier_lectures_recuperation(app, dossier_plfss2018, user_david):
    from zam_repondeur.models.events.dossier import LecturesRecuperees

    with transaction.manager:
        LecturesRecuperees.create(
            request=None, dossier=dossier_plfss2018, user=user_david
        )
        assert len(dossier_plfss2018.events) == 1

    resp = app.get("/dossiers/plfss-2018/journal", user=user_david)
    assert first_description_text(resp) == "Les lectures ont été récupérées."


def test_dossier_invitation_envoyee(app, dossier_plfss2018, user_david):
    from zam_repondeur.models.events.dossier import InvitationEnvoyee

    with transaction.manager:
        InvitationEnvoyee.create(
            request=None,
            dossier=dossier_plfss2018,
            user=user_david,
            email="foo@exemple.gouv.fr",
        )
        assert len(dossier_plfss2018.events) == 1

    resp = app.get("/dossiers/plfss-2018/journal", user=user_david)
    assert first_description_text(resp) == "David a invité « foo@exemple.gouv.fr »"
