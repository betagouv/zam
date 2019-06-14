import datetime
from operator import attrgetter


def test_get_dossiers_senat(mock_scraping_senat):
    from zam_repondeur.fetch.an.dossiers.models import (
        ChambreRef,
        DossierRef,
        LectureRef,
        TexteRef,
        TypeTexte,
    )
    from zam_repondeur.fetch.senat.scraping import get_dossiers_senat

    dossiers = get_dossiers_senat()

    assert set(dossiers.keys()) == {
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

    dossiers_values = sorted(dossiers.values(), key=attrgetter("uid"))
    assert dossiers_values == [
        DossierRef(
            uid="pjl18-404",
            titre="Organisation du système de santé",
            an_url="",
            senat_url="http://www.senat.fr/dossier-legislatif/pjl18-404.html",
            lectures=[
                LectureRef(
                    chambre=ChambreRef.SENAT,
                    titre="Première lecture – Commissions",
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
                    chambre=ChambreRef.SENAT,
                    titre="Première lecture – Séance publique",
                    texte=TexteRef(
                        uid="PJLSENAT2019X525",
                        type_=TypeTexte.PROJET,
                        chambre=ChambreRef.SENAT,
                        legislature=18,
                        numero=525,
                        titre_long="Texte de la commission déposé le 22 mai 2019",
                        titre_court="",
                        date_depot=datetime.date(2019, 5, 22),
                    ),
                    organe="PO78718",
                    partie=None,
                ),
                LectureRef(
                    chambre=ChambreRef.SENAT,
                    titre="Première lecture – Commissions",
                    texte=TexteRef(
                        uid="PJLSENAT2019X109",
                        type_=TypeTexte.PROJET,
                        chambre=ChambreRef.SENAT,
                        legislature=18,
                        numero=109,
                        titre_long="Texte modifié par le Sénat le 11 juin 2019",
                        titre_court="",
                        date_depot=datetime.date(2019, 6, 11),
                    ),
                    organe="",
                    partie=None,
                ),
            ],
        ),
        DossierRef(
            uid="pjl18-523",
            titre="Accord France Arménie",
            an_url="",
            senat_url="http://www.senat.fr/dossier-legislatif/pjl18-523.html",
            lectures=[
                LectureRef(
                    chambre=ChambreRef.SENAT,
                    titre="Première lecture – Commissions",
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
                ),
                LectureRef(
                    chambre=ChambreRef.SENAT,
                    titre="Première lecture – Séance publique",
                    texte=TexteRef(
                        uid="PJLSENAT2019X565",
                        type_=TypeTexte.PROJET,
                        chambre=ChambreRef.SENAT,
                        legislature=18,
                        numero=565,
                        titre_long="Texte de la commission déposé le 12 juin 2019",
                        titre_court="",
                        date_depot=datetime.date(2019, 6, 12),
                    ),
                    organe="PO78718",
                    partie=None,
                ),
            ],
        ),
        DossierRef(
            uid="pjl18-526",
            titre="Accords France-Suisse et France-Luxembourg",
            an_url="",
            senat_url="http://www.senat.fr/dossier-legislatif/pjl18-526.html",
            lectures=[
                LectureRef(
                    chambre=ChambreRef.SENAT,
                    titre="Première lecture – Commissions",
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
                    chambre=ChambreRef.SENAT,
                    titre="Première lecture – Séance publique",
                    texte=TexteRef(
                        uid="PJLSENAT2019X567",
                        type_=TypeTexte.PROJET,
                        chambre=ChambreRef.SENAT,
                        legislature=18,
                        numero=567,
                        titre_long="Texte de la commission déposé le 12 juin 2019",
                        titre_court="",
                        date_depot=datetime.date(2019, 6, 12),
                    ),
                    organe="PO78718",
                    partie=None,
                ),
            ],
        ),
        DossierRef(
            uid="pjl18-532",
            titre="Transformation de la fonction publique",
            an_url="",
            senat_url="http://www.senat.fr/dossier-legislatif/pjl18-532.html",
            lectures=[
                LectureRef(
                    chambre=ChambreRef.SENAT,
                    titre="Première lecture – Commissions",
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
                    chambre=ChambreRef.SENAT,
                    titre="Première lecture – Séance publique",
                    texte=TexteRef(
                        uid="PJLSENAT2019X571",
                        type_=TypeTexte.PROJET,
                        chambre=ChambreRef.SENAT,
                        legislature=18,
                        numero=571,
                        titre_long="Texte de la commission déposé le 12 juin 2019",
                        titre_court="",
                        date_depot=datetime.date(2019, 6, 12),
                    ),
                    organe="PO78718",
                    partie=None,
                ),
            ],
        ),
        DossierRef(
            uid="ppl17-699",
            titre="Instituer un médiateur territorial dans certaines collectivités",
            an_url="",
            senat_url="http://www.senat.fr/dossier-legislatif/ppl17-699.html",
            lectures=[
                LectureRef(
                    chambre=ChambreRef.SENAT,
                    titre="Première lecture – Commissions",
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
                ),
                LectureRef(
                    chambre=ChambreRef.SENAT,
                    titre="Première lecture – Séance publique",
                    texte=TexteRef(
                        uid="PPLSENAT2019X547",
                        type_=TypeTexte.PROPOSITION,
                        chambre=ChambreRef.SENAT,
                        legislature=17,
                        numero=547,
                        titre_long="Texte de la commission déposé le 5 juin 2019",
                        titre_court="",
                        date_depot=datetime.date(2019, 6, 5),
                    ),
                    organe="PO78718",
                    partie=None,
                ),
            ],
        ),
        DossierRef(
            uid="ppl18-002",
            titre="Agence nationale de la cohésion des territoires",
            an_url="",
            senat_url="http://www.senat.fr/dossier-legislatif/ppl18-002.html",
            lectures=[
                LectureRef(
                    chambre=ChambreRef.SENAT,
                    titre="Première lecture – Commissions",
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
                LectureRef(
                    chambre=ChambreRef.SENAT,
                    titre="Première lecture – Séance publique",
                    texte=TexteRef(
                        uid="PPLSENAT2018X99",
                        type_=TypeTexte.PROPOSITION,
                        chambre=ChambreRef.SENAT,
                        legislature=18,
                        numero=99,
                        titre_long="Texte de la commission déposé le 31 octobre 2018",
                        titre_court="",
                        date_depot=datetime.date(2018, 10, 31),
                    ),
                    organe="PO78718",
                    partie=None,
                ),
                LectureRef(
                    chambre=ChambreRef.SENAT,
                    titre="Première lecture – Commissions",
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
                    titre="Commission mixte paritaire (désaccord) : Texte résultat des travaux de la commission le 3 avril 2019 – Commissions",  # noqa
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
                    chambre=ChambreRef.SENAT,
                    titre="Nouvelle lecture – Commissions",
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
                    chambre=ChambreRef.SENAT,
                    titre="Nouvelle lecture – Séance publique",
                    texte=TexteRef(
                        uid="PPLSENAT2019X562",
                        type_=TypeTexte.PROPOSITION,
                        chambre=ChambreRef.SENAT,
                        legislature=18,
                        numero=562,
                        titre_long="Texte de la commission déposé le 12 juin 2019",
                        titre_court="",
                        date_depot=datetime.date(2019, 6, 12),
                    ),
                    organe="PO78718",
                    partie=None,
                ),
            ],
        ),
        DossierRef(
            uid="ppl18-043",
            titre="Directeur général de l'Agence nationale de la cohésion des territoires",  # noqa
            an_url="",
            senat_url="http://www.senat.fr/dossier-legislatif/ppl18-043.html",
            lectures=[
                LectureRef(
                    chambre=ChambreRef.SENAT,
                    titre="Première lecture – Commissions",
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
                LectureRef(
                    chambre=ChambreRef.SENAT,
                    titre="Première lecture – Séance publique",
                    texte=TexteRef(
                        uid="PPLSENAT2018X100",
                        type_=TypeTexte.PROPOSITION,
                        chambre=ChambreRef.SENAT,
                        legislature=18,
                        numero=100,
                        titre_long="Texte de la commission déposé le 31 octobre 2018",
                        titre_court="",
                        date_depot=datetime.date(2018, 10, 31),
                    ),
                    organe="PO78718",
                    partie=None,
                ),
                LectureRef(
                    chambre=ChambreRef.SENAT,
                    titre="Première lecture – Commissions",
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
                    titre="Commission mixte paritaire (accord) : Texte de la commission déposé le 3 avril 2019 – Séance publique",  # noqa
                    texte=TexteRef(
                        uid="PPLSENAT2019X432",
                        type_=TypeTexte.PROPOSITION,
                        chambre=ChambreRef.SENAT,
                        legislature=18,
                        numero=432,
                        titre_long="Texte de la commission déposé le 3 avril 2019",
                        titre_court="",
                        date_depot=datetime.date(2019, 4, 3),
                    ),
                    organe="PO78718",
                    partie=None,
                ),
            ],
        ),
        DossierRef(
            uid="ppl18-229",
            titre="Lutte contre l'habitat insalubre ou dangereux",
            an_url="",
            senat_url="http://www.senat.fr/dossier-legislatif/ppl18-229.html",
            lectures=[
                LectureRef(
                    chambre=ChambreRef.SENAT,
                    titre="Première lecture – Commissions",
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
                LectureRef(
                    chambre=ChambreRef.SENAT,
                    titre="Première lecture – Commissions",
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
                    titre="Première lecture – Séance publique",
                    texte=TexteRef(
                        uid="PPLSENAT2019X536",
                        type_=TypeTexte.PROPOSITION,
                        chambre=ChambreRef.SENAT,
                        legislature=18,
                        numero=536,
                        titre_long="Texte de la commission déposé le 29 mai 2019",
                        titre_court="",
                        date_depot=datetime.date(2019, 5, 29),
                    ),
                    organe="PO78718",
                    partie=None,
                ),
            ],
        ),
        DossierRef(
            uid="ppl18-260",
            titre="Accès à l'énergie et lutte contre la précarité énergétique",
            an_url="",
            senat_url="http://www.senat.fr/dossier-legislatif/ppl18-260.html",
            lectures=[
                LectureRef(
                    chambre=ChambreRef.SENAT,
                    titre="Première lecture – Commissions",
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
                LectureRef(
                    chambre=ChambreRef.SENAT,
                    titre="Première lecture – Commissions",
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
            ],
        ),
        DossierRef(
            uid="ppl18-305",
            titre="Création d'un statut de l'élu communal",
            an_url="",
            senat_url="http://www.senat.fr/dossier-legislatif/ppl18-305.html",
            lectures=[
                LectureRef(
                    chambre=ChambreRef.SENAT,
                    titre="Première lecture – Commissions",
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
                LectureRef(
                    chambre=ChambreRef.SENAT,
                    titre="Première lecture – Commissions",
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
            ],
        ),
        DossierRef(
            uid="ppl18-385",
            titre="Clarifier diverses dispositions du droit électoral",
            an_url="",
            senat_url="http://www.senat.fr/dossier-legislatif/ppl18-385.html",
            lectures=[
                LectureRef(
                    chambre=ChambreRef.SENAT,
                    titre="Première lecture – Commissions",
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
                ),
                LectureRef(
                    chambre=ChambreRef.SENAT,
                    titre="Première lecture – Séance publique",
                    texte=TexteRef(
                        uid="PPLSENAT2019X444",
                        type_=TypeTexte.PROPOSITION,
                        chambre=ChambreRef.SENAT,
                        legislature=18,
                        numero=444,
                        titre_long="Texte de la commission déposé le 10 avril 2019",
                        titre_court="",
                        date_depot=datetime.date(2019, 4, 10),
                    ),
                    organe="PO78718",
                    partie=None,
                ),
            ],
        ),
        DossierRef(
            uid="ppl18-386",
            titre="Clarifier diverses dispositions du droit électoral",
            an_url="",
            senat_url="http://www.senat.fr/dossier-legislatif/ppl18-386.html",
            lectures=[
                LectureRef(
                    chambre=ChambreRef.SENAT,
                    titre="Première lecture – Commissions",
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
                ),
                LectureRef(
                    chambre=ChambreRef.SENAT,
                    titre="Première lecture – Séance publique",
                    texte=TexteRef(
                        uid="PPLSENAT2019X445",
                        type_=TypeTexte.PROPOSITION,
                        chambre=ChambreRef.SENAT,
                        legislature=18,
                        numero=445,
                        titre_long="Texte de la commission déposé le 10 avril 2019",
                        titre_court="",
                        date_depot=datetime.date(2019, 4, 10),
                    ),
                    organe="PO78718",
                    partie=None,
                ),
            ],
        ),
        DossierRef(
            uid="ppl18-436",
            titre="Accès des PME à la commande publique",
            an_url="",
            senat_url="http://www.senat.fr/dossier-legislatif/ppl18-436.html",
            lectures=[
                LectureRef(
                    chambre=ChambreRef.SENAT,
                    titre="Première lecture – Commissions",
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
                LectureRef(
                    chambre=ChambreRef.SENAT,
                    titre="Première lecture – Commissions",
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
            ],
        ),
        DossierRef(
            uid="ppl18-454",
            titre="Exploitation des réseaux radioélectriques mobiles",
            an_url="",
            senat_url="http://www.senat.fr/dossier-legislatif/ppl18-454.html",
            lectures=[
                LectureRef(
                    chambre=ChambreRef.SENAT,
                    titre="Première lecture – Commissions",
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
                )
            ],
        ),
        DossierRef(
            uid="ppl18-462",
            titre="Participation des conseillers de Lyon aux élections sénatoriales",
            an_url="",
            senat_url="http://www.senat.fr/dossier-legislatif/ppl18-462.html",
            lectures=[
                LectureRef(
                    chambre=ChambreRef.SENAT,
                    titre="Première lecture – Commissions",
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
                ),
                LectureRef(
                    chambre=ChambreRef.SENAT,
                    titre="Première lecture – Séance publique",
                    texte=TexteRef(
                        uid="PPLSENAT2019X552",
                        type_=TypeTexte.PROPOSITION,
                        chambre=ChambreRef.SENAT,
                        legislature=18,
                        numero=552,
                        titre_long="Texte de la commission déposé le 5 juin 2019",
                        titre_court="",
                        date_depot=datetime.date(2019, 6, 5),
                    ),
                    organe="PO78718",
                    partie=None,
                ),
                LectureRef(
                    chambre=ChambreRef.SENAT,
                    titre="Première lecture – Commissions",
                    texte=TexteRef(
                        uid="PPLSENAT2019X108",
                        type_=TypeTexte.PROPOSITION,
                        chambre=ChambreRef.SENAT,
                        legislature=18,
                        numero=108,
                        titre_long="Texte adopté par le Sénat le 11 juin 2019",
                        titre_court="",
                        date_depot=datetime.date(2019, 6, 11),
                    ),
                    organe="",
                    partie=None,
                ),
            ],
        ),
        DossierRef(
            uid="ppr18-458",
            titre="Clarifier et actualiser le Règlement du Sénat",
            an_url="",
            senat_url="http://www.senat.fr/dossier-legislatif/ppr18-458.html",
            lectures=[
                LectureRef(
                    chambre=ChambreRef.SENAT,
                    titre="Première lecture – Commissions",
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
                ),
                LectureRef(
                    chambre=ChambreRef.SENAT,
                    titre="Première lecture – Séance publique",
                    texte=TexteRef(
                        uid="PPRSENAT2019X550",
                        type_=TypeTexte.PROPOSITION,
                        chambre=ChambreRef.SENAT,
                        legislature=18,
                        numero=550,
                        titre_long="Texte de la commission déposé le 5 juin 2019",
                        titre_court="",
                        date_depot=datetime.date(2019, 6, 5),
                    ),
                    organe="PO78718",
                    partie=None,
                ),
            ],
        ),
    ]


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


def test_create_dossier():
    from zam_repondeur.fetch.an.dossiers.models import (
        ChambreRef,
        DossierRef,
        LectureRef,
        TexteRef,
        TypeTexte,
    )
    from zam_repondeur.fetch.senat.scraping import create_dossier

    assert create_dossier(
        "pjl18-404", "/dossier-legislatif/rss/doslegpjl18-404.xml"
    ) == DossierRef(
        uid="pjl18-404",
        titre="Organisation du système de santé",
        an_url="",
        senat_url="http://www.senat.fr/dossier-legislatif/pjl18-404.html",
        lectures=[
            LectureRef(
                chambre=ChambreRef.SENAT,
                titre="Première lecture – Commissions",
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
                organe="",  # commission X
                partie=None,
            ),
            LectureRef(
                chambre=ChambreRef.SENAT,
                titre="Première lecture – Séance publique",
                texte=TexteRef(
                    uid="PJLSENAT2019X525",
                    type_=TypeTexte.PROJET,
                    chambre=ChambreRef.SENAT,
                    legislature=18,
                    numero=525,
                    titre_long="Texte de la commission déposé le 22 mai 2019",
                    titre_court="",
                    date_depot=datetime.date(2019, 5, 22),
                ),
                organe="PO78718",  # séance publique
                partie=None,
            ),
            LectureRef(
                chambre=ChambreRef.SENAT,
                titre="Première lecture – Commissions",
                texte=TexteRef(
                    uid="PJLSENAT2019X109",
                    type_=TypeTexte.PROJET,
                    chambre=ChambreRef.SENAT,
                    legislature=18,
                    numero=109,
                    titre_long="Texte modifié par le Sénat le 11 juin 2019",
                    titre_court="",
                    date_depot=datetime.date(2019, 6, 11),
                ),
                organe="",
                partie=None,
            ),
        ],
    )
