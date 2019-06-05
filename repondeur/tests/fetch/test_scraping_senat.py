import datetime
from pathlib import Path

import responses


@responses.activate
def test_get_dossiers_senat():
    from zam_repondeur.fetch.an.dossiers.models import (
        ChambreRef,
        DossierRef,
        LectureRef,
        TexteRef,
        TypeTexte,
    )
    from zam_repondeur.fetch.senat.scraping import get_dossiers_senat

    pids = {
        "ppl18-462",
        "ppl18-260",
        "ppl18-385",
        "ppl18-043",
        "pjl18-532",
        "ppl18-002",
        "ppl18-229",
        "pjl18-404",
        "pjl18-523",
        "ppl18-305",
        "ppr18-458",
        "pjl18-526",
        "ppl18-386",
        "ppl18-454",
        "ppl17-699",
        "ppl18-436",
    }
    responses.add(
        responses.GET,
        f"http://www.senat.fr/dossiers-legislatifs/textes-recents.html",
        body=(
            Path(__file__).parent / "sample_data" / "senat" / "textes-recents.html"
        ).read_text("utf-8", "ignore"),
        status=200,
    )
    for pid in pids:
        responses.add(
            responses.GET,
            f"http://www.senat.fr/dossier-legislatif/rss/dosleg{pid}.xml",
            body=(Path(__file__).parent / "sample_data" / "senat" / f"dosleg{pid}.xml")
            .read_text("utf-8")
            .encode("latin-1"),
            status=200,
        )

    dossiers = get_dossiers_senat()
    assert set(dossiers.keys()) == pids
    dossiers_values = dossiers.values()
    assert (
        DossierRef(
            uid="pjl18-532",
            titre="Transformation de la fonction publique",
            lectures=[
                LectureRef(
                    chambre=ChambreRef.SENAT,
                    titre="Première lecture",
                    texte=TexteRef(
                        uid="PJLSENAT2019X532",
                        type_=TypeTexte.PROJET,
                        chambre=ChambreRef.SENAT,
                        legislature=18,
                        numero=532,
                        titre_long="Texte transmis au Sénat le 29 mai 2019",
                        titre_court="",
                        date_depot=datetime.date(2019, 5, 29),
                    ),
                    organe="",
                    partie=None,
                ),
                LectureRef(
                    chambre=ChambreRef.AN,
                    titre="Première lecture",
                    texte=TexteRef(
                        uid="PJLAN2019X279",
                        type_=TypeTexte.PROJET,
                        chambre=ChambreRef.AN,
                        legislature=18,
                        numero=279,
                        titre_long="Texte adopté par l'Assemblée nationale le 28 mai 2019",  # noqa
                        titre_court="",
                        date_depot=datetime.date(2019, 5, 28),
                    ),
                    organe="",
                    partie=None,
                ),
                LectureRef(
                    chambre=ChambreRef.AN,
                    titre="Première lecture",
                    texte=TexteRef(
                        uid="PJLAN2019X1802",
                        type_=TypeTexte.PROJET,
                        chambre=ChambreRef.AN,
                        legislature=18,
                        numero=1802,
                        titre_long="Texte de MM. Gérald DARMANIN, ministre de l'Action et des comptes publics et Olivier DUSSOPT,  déposé à l'Assemblée Nationale le 27 mars 2019",  # noqa
                        titre_court="",
                        date_depot=datetime.date(2019, 3, 27),
                    ),
                    organe="",
                    partie=None,
                ),
            ],
        )
        in dossiers_values
    )
    assert (
        DossierRef(
            uid="ppl18-260",
            titre="Accès à l'énergie et lutte contre la précarité énergétique",
            lectures=[
                LectureRef(
                    chambre=ChambreRef.SENAT,
                    titre="Première lecture",
                    texte=TexteRef(
                        uid="PPLSENAT2019X538",
                        type_=TypeTexte.PROPOSITION,
                        chambre=ChambreRef.SENAT,
                        legislature=18,
                        numero=538,
                        titre_long="Texte résultat des travaux de la commission le 29 mai 2019",  # noqa
                        titre_court="",
                        date_depot=datetime.date(2019, 5, 29),
                    ),
                    organe="",
                    partie=None,
                ),
                LectureRef(
                    chambre=ChambreRef.SENAT,
                    titre="Première lecture",
                    texte=TexteRef(
                        uid="PPLSENAT2019X260",
                        type_=TypeTexte.PROPOSITION,
                        chambre=ChambreRef.SENAT,
                        legislature=18,
                        numero=260,
                        titre_long="Texte de M. Fabien GAY, Mme Éliane ASSASSI et plusieurs de leurs collègues,  déposé au Sénat le 22 janvier 2019",  # noqa
                        titre_court="",
                        date_depot=datetime.date(2019, 1, 22),
                    ),
                    organe="",
                    partie=None,
                ),
            ],
        )
        in dossiers_values
    )
    assert (
        DossierRef(
            uid="ppl18-043",
            titre="Directeur général de l'Agence nationale de la cohésion des territoires",  # noqa
            lectures=[
                LectureRef(
                    chambre=ChambreRef.AN,
                    titre="Première lecture",
                    texte=TexteRef(
                        uid="PPLAN2019X243",
                        type_=TypeTexte.PROPOSITION,
                        chambre=ChambreRef.AN,
                        legislature=18,
                        numero=243,
                        titre_long="Texte modifié par l'Assemblée nationale le 12 mars 2019",  # noqa
                        titre_court="",
                        date_depot=datetime.date(2019, 3, 12),
                    ),
                    organe="",
                    partie=None,
                ),
                LectureRef(
                    chambre=ChambreRef.AN,
                    titre="Première lecture",
                    texte=TexteRef(
                        uid="PPLAN2018X1394",
                        type_=TypeTexte.PROPOSITION,
                        chambre=ChambreRef.AN,
                        legislature=18,
                        numero=1394,
                        titre_long="Texte transmis à l'Assemblée nationale le 9 novembre 2018",  # noqa
                        titre_court="",
                        date_depot=datetime.date(2018, 11, 9),
                    ),
                    organe="",
                    partie=None,
                ),
                LectureRef(
                    chambre=ChambreRef.SENAT,
                    titre="Première lecture",
                    texte=TexteRef(
                        uid="PPLSENAT2018X21",
                        type_=TypeTexte.PROPOSITION,
                        chambre=ChambreRef.SENAT,
                        legislature=18,
                        numero=21,
                        titre_long="Texte adopté par le Sénat le 8 novembre 2018",
                        titre_court="",
                        date_depot=datetime.date(2018, 11, 8),
                    ),
                    organe="",
                    partie=None,
                ),
                LectureRef(
                    chambre=ChambreRef.SENAT,
                    titre="Première lecture",
                    texte=TexteRef(
                        uid="PPLSENAT2018X43",
                        type_=TypeTexte.PROPOSITION,
                        chambre=ChambreRef.SENAT,
                        legislature=18,
                        numero=43,
                        titre_long="Texte de MM. Hervé MAUREY et Jean-Claude REQUIER,  déposé au Sénat le 16 octobre 2018",  # noqa
                        titre_court="",
                        date_depot=datetime.date(2018, 10, 16),
                    ),
                    organe="",
                    partie=None,
                ),
            ],
        )
        in dossiers_values
    )
    assert (
        DossierRef(
            uid="ppl18-305",
            titre="Création d'un statut de l'élu communal",
            lectures=[
                LectureRef(
                    chambre=ChambreRef.SENAT,
                    titre="Première lecture",
                    texte=TexteRef(
                        uid="PPLSENAT2019X534",
                        type_=TypeTexte.PROPOSITION,
                        chambre=ChambreRef.SENAT,
                        legislature=18,
                        numero=534,
                        titre_long="Texte résultat des travaux de la commission le 29 mai 2019",  # noqa
                        titre_court="",
                        date_depot=datetime.date(2019, 5, 29),
                    ),
                    organe="",
                    partie=None,
                ),
                LectureRef(
                    chambre=ChambreRef.SENAT,
                    titre="Première lecture",
                    texte=TexteRef(
                        uid="PPLSENAT2019X305",
                        type_=TypeTexte.PROPOSITION,
                        chambre=ChambreRef.SENAT,
                        legislature=18,
                        numero=305,
                        titre_long="Texte de M. Pierre-Yves COLLOMBAT et plusieurs de ses collègues,  déposé au Sénat le 12 février 2019",  # noqa
                        titre_court="",
                        date_depot=datetime.date(2019, 2, 12),
                    ),
                    organe="",
                    partie=None,
                ),
            ],
        )
        in dossiers_values
    )
    assert (
        DossierRef(
            uid="ppl18-385",
            titre="Clarifier diverses dispositions du droit électoral",
            lectures=[
                LectureRef(
                    chambre=ChambreRef.SENAT,
                    titre="Première lecture",
                    texte=TexteRef(
                        uid="PPLSENAT2019X385",
                        type_=TypeTexte.PROPOSITION,
                        chambre=ChambreRef.SENAT,
                        legislature=18,
                        numero=385,
                        titre_long="Texte de M. Alain RICHARD et plusieurs de ses collègues,  déposé au Sénat le 19 mars 2019",  # noqa
                        titre_court="",
                        date_depot=datetime.date(2019, 3, 19),
                    ),
                    organe="",
                    partie=None,
                )
            ],
        )
        in dossiers_values
    )
    assert (
        DossierRef(
            uid="ppl18-386",
            titre="Clarifier diverses dispositions du droit électoral",
            lectures=[
                LectureRef(
                    chambre=ChambreRef.SENAT,
                    titre="Première lecture",
                    texte=TexteRef(
                        uid="PPLSENAT2019X386",
                        type_=TypeTexte.PROPOSITION,
                        chambre=ChambreRef.SENAT,
                        legislature=18,
                        numero=386,
                        titre_long="Texte de M. Alain RICHARD et plusieurs de ses collègues,  déposé au Sénat le 19 mars 2019",  # noqa
                        titre_court="",
                        date_depot=datetime.date(2019, 3, 19),
                    ),
                    organe="",
                    partie=None,
                )
            ],
        )
        in dossiers_values
    )
    assert (
        DossierRef(
            uid="ppl18-229",
            titre="Lutte contre l'habitat insalubre ou dangereux",
            lectures=[
                LectureRef(
                    chambre=ChambreRef.SENAT,
                    titre="Première lecture",
                    texte=TexteRef(
                        uid="PPLSENAT2019X326",
                        type_=TypeTexte.PROPOSITION,
                        chambre=ChambreRef.SENAT,
                        legislature=18,
                        numero=326,
                        titre_long="Texte résultat des travaux de la commission le 20 février 2019",  # noqa
                        titre_court="",
                        date_depot=datetime.date(2019, 2, 20),
                    ),
                    organe="",
                    partie=None,
                ),
                LectureRef(
                    chambre=ChambreRef.SENAT,
                    titre="Première lecture",
                    texte=TexteRef(
                        uid="PPLSENAT2018X229",
                        type_=TypeTexte.PROPOSITION,
                        chambre=ChambreRef.SENAT,
                        legislature=18,
                        numero=229,
                        titre_long="Texte de M. Bruno GILLES et plusieurs de ses collègues,  déposé au Sénat le 20 décembre 2018",  # noqa
                        titre_court="",
                        date_depot=datetime.date(2018, 12, 20),
                    ),
                    organe="",
                    partie=None,
                ),
            ],
        )
        in dossiers_values
    )
    assert (
        DossierRef(
            uid="ppl18-454",
            titre="Exploitation des réseaux radioélectriques mobiles",
            lectures=[
                LectureRef(
                    chambre=ChambreRef.SENAT,
                    titre="Première lecture",
                    texte=TexteRef(
                        uid="PPLSENAT2019X454",
                        type_=TypeTexte.PROPOSITION,
                        chambre=ChambreRef.SENAT,
                        legislature=18,
                        numero=454,
                        titre_long="Texte transmis au Sénat le 11 avril 2019",
                        titre_court="",
                        date_depot=datetime.date(2019, 4, 11),
                    ),
                    organe="",
                    partie=None,
                ),
                LectureRef(
                    chambre=ChambreRef.AN,
                    titre="Première lecture",
                    texte=TexteRef(
                        uid="PPLAN2019X257",
                        type_=TypeTexte.PROPOSITION,
                        chambre=ChambreRef.AN,
                        legislature=18,
                        numero=257,
                        titre_long="Texte adopté par l'Assemblée nationale le 10 avril 2019",  # noqa
                        titre_court="",
                        date_depot=datetime.date(2019, 4, 10),
                    ),
                    organe="",
                    partie=None,
                ),
                LectureRef(
                    chambre=ChambreRef.AN,
                    titre="Première lecture",
                    texte=TexteRef(
                        uid="PPLAN2019X1722",
                        type_=TypeTexte.PROPOSITION,
                        chambre=ChambreRef.AN,
                        legislature=18,
                        numero=1722,
                        titre_long="Texte de MM. Gilles LE GENDRE, Eric BOTHOREL, Mme Célia DE LAVERGNE, M. Roland LESCURE et Mme Amélie DE MONTCHALIN,  déposé à l'Assemblée Nationale le 20 février 2019",  # noqa
                        titre_court="",
                        date_depot=datetime.date(2019, 2, 20),
                    ),
                    organe="",
                    partie=None,
                ),
            ],
        )
        in dossiers_values
    )
    assert (
        DossierRef(
            uid="ppl18-002",
            titre="Agence nationale de la cohésion des territoires",
            lectures=[
                LectureRef(
                    chambre=ChambreRef.SENAT,
                    titre="Nouvelle lecture",
                    texte=TexteRef(
                        uid="PPLSENAT2019X518",
                        type_=TypeTexte.PROPOSITION,
                        chambre=ChambreRef.SENAT,
                        legislature=18,
                        numero=518,
                        titre_long="Texte transmis au Sénat le 21 mai 2019",
                        titre_court="",
                        date_depot=datetime.date(2019, 5, 21),
                    ),
                    organe="",
                    partie=None,
                ),
                LectureRef(
                    chambre=ChambreRef.AN,
                    titre="Nouvelle lecture",
                    texte=TexteRef(
                        uid="PPLAN2019X273",
                        type_=TypeTexte.PROPOSITION,
                        chambre=ChambreRef.AN,
                        legislature=18,
                        numero=273,
                        titre_long="Texte adopté par l'Assemblée nationale le 21 mai 2019",  # noqa
                        titre_court="",
                        date_depot=datetime.date(2019, 5, 21),
                    ),
                    organe="",
                    partie=None,
                ),
                LectureRef(
                    chambre=ChambreRef.AN,
                    titre="Nouvelle lecture",
                    texte=TexteRef(
                        uid="PPLAN2019X1839",
                        type_=TypeTexte.PROPOSITION,
                        chambre=ChambreRef.AN,
                        legislature=18,
                        numero=1839,
                        titre_long="Texte transmis à l'Assemblée nationale le 4 avril 2019",  # noqa
                        titre_court="",
                        date_depot=datetime.date(2019, 4, 4),
                    ),
                    organe="",
                    partie=None,
                ),
                LectureRef(
                    chambre=ChambreRef.SENAT,
                    titre="Commission mixte paritaire (désaccord) : Texte résultat des travaux de la commission le 3 avril 2019",  # noqa
                    texte=TexteRef(
                        uid="PPLSENAT2019X434",
                        type_=TypeTexte.PROPOSITION,
                        chambre=ChambreRef.SENAT,
                        legislature=18,
                        numero=434,
                        titre_long="Texte résultat des travaux de la commission le 3 avril 2019",  # noqa
                        titre_court="",
                        date_depot=datetime.date(2019, 4, 3),
                    ),
                    organe="",
                    partie=None,
                ),
                LectureRef(
                    chambre=ChambreRef.AN,
                    titre="Première lecture",
                    texte=TexteRef(
                        uid="PPLAN2019X242",
                        type_=TypeTexte.PROPOSITION,
                        chambre=ChambreRef.AN,
                        legislature=18,
                        numero=242,
                        titre_long="Texte modifié par l'Assemblée nationale le 12 mars 2019",  # noqa
                        titre_court="",
                        date_depot=datetime.date(2019, 3, 12),
                    ),
                    organe="",
                    partie=None,
                ),
                LectureRef(
                    chambre=ChambreRef.AN,
                    titre="Première lecture",
                    texte=TexteRef(
                        uid="PPLAN2018X1393",
                        type_=TypeTexte.PROPOSITION,
                        chambre=ChambreRef.AN,
                        legislature=18,
                        numero=1393,
                        titre_long="Texte transmis à l'Assemblée nationale le 9 novembre 2018",  # noqa
                        titre_court="",
                        date_depot=datetime.date(2018, 11, 9),
                    ),
                    organe="",
                    partie=None,
                ),
                LectureRef(
                    chambre=ChambreRef.SENAT,
                    titre="Première lecture",
                    texte=TexteRef(
                        uid="PPLSENAT2018X20",
                        type_=TypeTexte.PROPOSITION,
                        chambre=ChambreRef.SENAT,
                        legislature=18,
                        numero=20,
                        titre_long="Texte adopté par le Sénat le 8 novembre 2018",
                        titre_court="",
                        date_depot=datetime.date(2018, 11, 8),
                    ),
                    organe="",
                    partie=None,
                ),
                LectureRef(
                    chambre=ChambreRef.SENAT,
                    titre="Première lecture",
                    texte=TexteRef(
                        uid="PPLSENAT2018X2",
                        type_=TypeTexte.PROPOSITION,
                        chambre=ChambreRef.SENAT,
                        legislature=18,
                        numero=2,
                        titre_long="Texte de M. Jean-Claude REQUIER et plusieurs de ses collègues,  déposé au Sénat le 2 octobre 2018",  # noqa
                        titre_court="",
                        date_depot=datetime.date(2018, 10, 2),
                    ),
                    organe="",
                    partie=None,
                ),
            ],
        )
        in dossiers_values
    )
    assert (
        DossierRef(
            uid="ppr18-458",
            titre="Clarifier et actualiser le Règlement du Sénat",
            lectures=[
                LectureRef(
                    chambre=ChambreRef.SENAT,
                    titre="Première lecture",
                    texte=TexteRef(
                        uid="PPRSENAT2019X458",
                        type_=TypeTexte.PROPOSITION,
                        chambre=ChambreRef.SENAT,
                        legislature=18,
                        numero=458,
                        titre_long="Texte de M. Gérard LARCHER, Président du Sénat,  déposé au Sénat le 12 avril 2019",  # noqa
                        titre_court="",
                        date_depot=datetime.date(2019, 4, 12),
                    ),
                    organe="",
                    partie=None,
                )
            ],
        )
        in dossiers_values
    )
    assert (
        DossierRef(
            uid="ppl18-462",
            titre="Participation des conseillers de Lyon aux élections sénatoriales",
            lectures=[
                LectureRef(
                    chambre=ChambreRef.SENAT,
                    titre="Première lecture",
                    texte=TexteRef(
                        uid="PPLSENAT2019X462",
                        type_=TypeTexte.PROPOSITION,
                        chambre=ChambreRef.SENAT,
                        legislature=18,
                        numero=462,
                        titre_long="Texte de M. François-Noël BUFFET et plusieurs de ses collègues,  déposé au Sénat le 16 avril 2019",  # noqa
                        titre_court="",
                        date_depot=datetime.date(2019, 4, 16),
                    ),
                    organe="",
                    partie=None,
                )
            ],
        )
        in dossiers_values
    )
    assert (
        DossierRef(
            uid="ppl18-436",
            titre="Accès des PME à la commande publique",
            lectures=[
                LectureRef(
                    chambre=ChambreRef.SENAT,
                    titre="Première lecture",
                    texte=TexteRef(
                        uid="PPLSENAT2019X531",
                        type_=TypeTexte.PROPOSITION,
                        chambre=ChambreRef.SENAT,
                        legislature=18,
                        numero=531,
                        titre_long="Texte résultat des travaux de la commission le 29 mai 2019",  # noqa
                        titre_court="",
                        date_depot=datetime.date(2019, 5, 29),
                    ),
                    organe="",
                    partie=None,
                ),
                LectureRef(
                    chambre=ChambreRef.SENAT,
                    titre="Première lecture",
                    texte=TexteRef(
                        uid="PPLSENAT2019X436",
                        type_=TypeTexte.PROPOSITION,
                        chambre=ChambreRef.SENAT,
                        legislature=18,
                        numero=436,
                        titre_long="Texte de MM. Jean-Marc GABOUTY, Jean-Claude REQUIER et plusieurs de leurs collègues,  déposé au Sénat le 4 avril 2019",  # noqa
                        titre_court="",
                        date_depot=datetime.date(2019, 4, 4),
                    ),
                    organe="",
                    partie=None,
                ),
            ],
        )
        in dossiers_values
    )
    assert (
        DossierRef(
            uid="pjl18-404",
            titre="Organisation du système de santé",
            lectures=[
                LectureRef(
                    chambre=ChambreRef.SENAT,
                    titre="Première lecture",
                    texte=TexteRef(
                        uid="PJLSENAT2019X404",
                        type_=TypeTexte.PROJET,
                        chambre=ChambreRef.SENAT,
                        legislature=18,
                        numero=404,
                        titre_long="Texte transmis au Sénat le 26 mars 2019",
                        titre_court="",
                        date_depot=datetime.date(2019, 3, 26),
                    ),
                    organe="",
                    partie=None,
                ),
                LectureRef(
                    chambre=ChambreRef.AN,
                    titre="Première lecture",
                    texte=TexteRef(
                        uid="PJLAN2019X245",
                        type_=TypeTexte.PROJET,
                        chambre=ChambreRef.AN,
                        legislature=18,
                        numero=245,
                        titre_long="Texte adopté par l'Assemblée nationale le 26 mars 2019",  # noqa
                        titre_court="",
                        date_depot=datetime.date(2019, 3, 26),
                    ),
                    organe="",
                    partie=None,
                ),
                LectureRef(
                    chambre=ChambreRef.AN,
                    titre="Première lecture",
                    texte=TexteRef(
                        uid="PJLAN2019X1681",
                        type_=TypeTexte.PROJET,
                        chambre=ChambreRef.AN,
                        legislature=18,
                        numero=1681,
                        titre_long="Texte de Mme Agnès BUZYN, ministre des Solidarités et de la Santé,  déposé à l'Assemblée Nationale le 13 février 2019",  # noqa
                        titre_court="",
                        date_depot=datetime.date(2019, 2, 13),
                    ),
                    organe="",
                    partie=None,
                ),
            ],
        )
        in dossiers_values
    )
    assert (
        DossierRef(
            uid="pjl18-523",
            titre="Accord France Arménie",
            lectures=[
                LectureRef(
                    chambre=ChambreRef.SENAT,
                    titre="Première lecture",
                    texte=TexteRef(
                        uid="PJLSENAT2019X523",
                        type_=TypeTexte.PROJET,
                        chambre=ChambreRef.SENAT,
                        legislature=18,
                        numero=523,
                        titre_long="Texte de M. Jean-Yves LE DRIAN, ministre de l'Europe et des affaires étrangères,  déposé au Sénat le 22 mai 2019",  # noqa
                        titre_court="",
                        date_depot=datetime.date(2019, 5, 22),
                    ),
                    organe="",
                    partie=None,
                )
            ],
        )
        in dossiers_values
    )
    assert (
        DossierRef(
            uid="ppl17-699",
            titre="Instituer un médiateur territorial dans certaines collectivités",
            lectures=[
                LectureRef(
                    chambre=ChambreRef.SENAT,
                    titre="Première lecture",
                    texte=TexteRef(
                        uid="PPLSENAT2018X699",
                        type_=TypeTexte.PROPOSITION,
                        chambre=ChambreRef.SENAT,
                        legislature=17,
                        numero=699,
                        titre_long="Texte de Mme Nathalie DELATTRE, M. François PILLET et plusieurs de leurs collègues,  déposé au Sénat le 30 juillet 2018",  # noqa
                        titre_court="",
                        date_depot=datetime.date(2018, 7, 30),
                    ),
                    organe="",
                    partie=None,
                )
            ],
        )
        in dossiers_values
    )
    assert (
        DossierRef(
            uid="pjl18-526",
            titre="Accords France-Suisse et France-Luxembourg",
            lectures=[
                LectureRef(
                    chambre=ChambreRef.SENAT,
                    titre="Première lecture",
                    texte=TexteRef(
                        uid="PJLSENAT2019X526",
                        type_=TypeTexte.PROJET,
                        chambre=ChambreRef.SENAT,
                        legislature=18,
                        numero=526,
                        titre_long="Texte transmis au Sénat le 24 mai 2019",
                        titre_court="",
                        date_depot=datetime.date(2019, 5, 24),
                    ),
                    organe="",
                    partie=None,
                ),
                LectureRef(
                    chambre=ChambreRef.AN,
                    titre="Première lecture",
                    texte=TexteRef(
                        uid="PJLAN2019X278",
                        type_=TypeTexte.PROJET,
                        chambre=ChambreRef.AN,
                        legislature=18,
                        numero=278,
                        titre_long="Texte adopté par l'Assemblée nationale le 23 mai 2019",  # noqa
                        titre_court="",
                        date_depot=datetime.date(2019, 5, 23),
                    ),
                    organe="",
                    partie=None,
                ),
                LectureRef(
                    chambre=ChambreRef.AN,
                    titre="Première lecture",
                    texte=TexteRef(
                        uid="PJLAN2017X390",
                        type_=TypeTexte.PROJET,
                        chambre=ChambreRef.AN,
                        legislature=18,
                        numero=390,
                        titre_long="Texte de M. Jean-Yves LE DRIAN, ministre de l'Europe et des affaires étrangères,  déposé à l'Assemblée Nationale le 22 novembre 2017",  # noqa
                        titre_court="",
                        date_depot=datetime.date(2017, 11, 22),
                    ),
                    organe="",
                    partie=None,
                ),
            ],
        )
        in dossiers_values
    )


def test_extract_recent_urls():
    from zam_repondeur.fetch.senat.scraping import (
        download_textes_recents,
        extract_recent_urls,
    )

    assert extract_recent_urls(download_textes_recents()) == {
        "/dossier-legislatif/pjl18-404.html",
        "/dossier-legislatif/pjl18-523.html",
        "/dossier-legislatif/pjl18-526.html",
        "/dossier-legislatif/pjl18-532.html",
        "/dossier-legislatif/ppl17-699.html",
        "/dossier-legislatif/ppl18-002.html",
        "/dossier-legislatif/ppl18-043.html",
        "/dossier-legislatif/ppl18-229.html",
        "/dossier-legislatif/ppl18-260.html",
        "/dossier-legislatif/ppl18-305.html",
        "/dossier-legislatif/ppl18-385.html",
        "/dossier-legislatif/ppl18-386.html",
        "/dossier-legislatif/ppl18-436.html",
        "/dossier-legislatif/ppl18-454.html",
        "/dossier-legislatif/ppl18-462.html",
        "/dossier-legislatif/ppr18-458.html",
    }


def test_convert_to_rss_urls():
    from zam_repondeur.fetch.senat.scraping import (
        download_textes_recents,
        extract_recent_urls,
        convert_to_rss_urls,
    )

    assert convert_to_rss_urls(extract_recent_urls(download_textes_recents())) == {
        "pjl18-404": "/dossier-legislatif/rss/doslegpjl18-404.xml",
        "pjl18-523": "/dossier-legislatif/rss/doslegpjl18-523.xml",
        "pjl18-526": "/dossier-legislatif/rss/doslegpjl18-526.xml",
        "pjl18-532": "/dossier-legislatif/rss/doslegpjl18-532.xml",
        "ppl17-699": "/dossier-legislatif/rss/doslegppl17-699.xml",
        "ppl18-002": "/dossier-legislatif/rss/doslegppl18-002.xml",
        "ppl18-043": "/dossier-legislatif/rss/doslegppl18-043.xml",
        "ppl18-229": "/dossier-legislatif/rss/doslegppl18-229.xml",
        "ppl18-260": "/dossier-legislatif/rss/doslegppl18-260.xml",
        "ppl18-305": "/dossier-legislatif/rss/doslegppl18-305.xml",
        "ppl18-385": "/dossier-legislatif/rss/doslegppl18-385.xml",
        "ppl18-386": "/dossier-legislatif/rss/doslegppl18-386.xml",
        "ppl18-436": "/dossier-legislatif/rss/doslegppl18-436.xml",
        "ppl18-454": "/dossier-legislatif/rss/doslegppl18-454.xml",
        "ppl18-462": "/dossier-legislatif/rss/doslegppl18-462.xml",
        "ppr18-458": "/dossier-legislatif/rss/doslegppr18-458.xml",
    }


@responses.activate
def test_create_dossier():
    from zam_repondeur.fetch.an.dossiers.models import (
        ChambreRef,
        DossierRef,
        LectureRef,
        TexteRef,
        TypeTexte,
    )
    from zam_repondeur.fetch.senat.scraping import create_dossier

    responses.add(
        responses.GET,
        "http://www.senat.fr/dossier-legislatif/rss/doslegpjl18-404.xml",
        body=(Path(__file__).parent / "sample_data" / "senat" / "doslegpjl18-404.xml")
        .read_text("utf-8")
        .encode("latin-1"),
        status=200,
    )
    assert create_dossier(
        "pjl18-404", "/dossier-legislatif/rss/doslegpjl18-404.xml"
    ) == DossierRef(
        uid="pjl18-404",
        titre="Organisation du système de santé",
        lectures=[
            LectureRef(
                chambre=ChambreRef.SENAT,
                titre="Première lecture",
                texte=TexteRef(
                    uid="PJLSENAT2019X404",
                    type_=TypeTexte.PROJET,
                    chambre=ChambreRef.SENAT,
                    legislature=18,
                    numero=404,
                    titre_long="Texte transmis au Sénat le 26 mars 2019",
                    titre_court="",
                    date_depot=datetime.date(2019, 3, 26),
                ),
                organe="",
                partie=None,
            ),
            LectureRef(
                chambre=ChambreRef.AN,
                titre="Première lecture",
                texte=TexteRef(
                    uid="PJLAN2019X245",
                    type_=TypeTexte.PROJET,
                    chambre=ChambreRef.AN,
                    legislature=18,
                    numero=245,
                    titre_long="Texte adopté par l'Assemblée nationale le 26 mars 2019",
                    titre_court="",
                    date_depot=datetime.date(2019, 3, 26),
                ),
                organe="",
                partie=None,
            ),
            LectureRef(
                chambre=ChambreRef.AN,
                titre="Première lecture",
                texte=TexteRef(
                    uid="PJLAN2019X1681",
                    type_=TypeTexte.PROJET,
                    chambre=ChambreRef.AN,
                    legislature=18,
                    numero=1681,
                    titre_long="Texte de Mme Agnès BUZYN, ministre des Solidarités et de la Santé,  déposé à l'Assemblée Nationale le 13 février 2019",  # noqa
                    titre_court="",
                    date_depot=datetime.date(2019, 2, 13),
                ),
                organe="",
                partie=None,
            ),
        ],
    )
