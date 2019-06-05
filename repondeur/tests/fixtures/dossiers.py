from datetime import date
from unittest.mock import patch

import pytest


@pytest.yield_fixture(scope="session", autouse=True)
def mock_dossiers():
    from zam_repondeur.fetch.an.dossiers.models import (
        ChambreRef,
        DossierRef,
        LectureRef,
        TexteRef,
        TypeTexte,
    )

    with patch("zam_repondeur.data.get_dossiers_legislatifs") as m_dossiers:
        m_dossiers.return_value = {
            "DLR5L15N36030": DossierRef(
                uid="DLR5L15N36030",
                titre="Sécurité sociale : loi de financement 2018",
                an_url="http://www.assemblee-nationale.fr/dyn/15/dossiers/alt/plfss_2018",  # noqa
                senat_url="http://www.senat.fr/dossier-legislatif/plfss2018.html",
                lectures=[
                    LectureRef(
                        chambre=ChambreRef.AN,
                        titre="Première lecture – Titre lecture",
                        texte=TexteRef(
                            uid="PRJLANR5L15B0269",
                            type_=TypeTexte.PROJET,
                            chambre=ChambreRef.AN,
                            legislature=15,
                            numero=269,
                            titre_long="projet de loi de financement de la sécurité sociale pour 2018",  # noqa
                            titre_court="PLFSS pour 2018",
                            date_depot=date(2017, 10, 11),
                        ),
                        organe="PO717460",  # séance publique
                    ),
                    LectureRef(
                        chambre=ChambreRef.SENAT,
                        titre="Première lecture – Titre lecture",
                        texte=TexteRef(
                            uid="PRJLSNR5S299B0063",
                            type_=TypeTexte.PROJET,
                            chambre=ChambreRef.SENAT,
                            legislature=2017,
                            numero=63,
                            titre_long="projet de loi de financement de la sécurité sociale pour 2018",  # noqa
                            titre_court="PLFSS pour 2018",
                            date_depot=date(2017, 11, 6),
                        ),
                        organe="PO78718",  # séance publique
                    ),
                ],
            ),
            "DLR5L15N36159": DossierRef(
                uid="DLR5L15N36159",
                titre="Fonction publique : un Etat au service d'une société de confiance",  # noqa
                an_url="http://www.assemblee-nationale.fr/dyn/15/dossiers/alt/etat_service_societe_confiance",  # noqa
                senat_url="http://www.senat.fr/dossier-legislatif/pjl17-259.html",
                lectures=[
                    LectureRef(
                        chambre=ChambreRef.AN,
                        titre="Nouvelle lecture – Titre lecture",
                        texte=TexteRef(
                            uid="PRJLANR5L15B0806",
                            type_=TypeTexte.PROJET,
                            chambre=ChambreRef.AN,
                            legislature=15,
                            numero=806,
                            titre_long="projet de loi renforçant l'efficacité de l'administration pour une relation de confiance avec le public",  # noqa
                            titre_court="Renforcement de l'efficacité de l'administration pour une relation de confiance avec le public",  # noqa
                            date_depot=date(2018, 3, 21),
                        ),
                        organe="PO744107",  # commission spéciale
                    )
                ],
            ),
            "DLR5L15N36892": DossierRef(
                uid="DLR5L15N36892",
                titre="Sécurité sociale : loi de financement 2019",
                an_url="http://www.assemblee-nationale.fr/dyn/15/dossiers/alt/plfss_2019",  # noqa
                senat_url="http://www.senat.fr/dossier-legislatif/plfss2019.html",
                lectures=[
                    LectureRef(
                        chambre=ChambreRef.SENAT,
                        titre="Première lecture – Titre lecture",
                        texte=TexteRef(
                            uid="PRJLSNR5S319B0106",
                            type_=TypeTexte.PROJET,
                            chambre=ChambreRef.SENAT,
                            legislature=None,
                            numero=106,
                            titre_long="projet de loi de financement de la sécurité sociale pour 2019",  # noqa
                            titre_court="PLFSS pour 2019",
                            date_depot=date(2018, 11, 5),
                        ),
                        organe="PO78718",  # séance publique
                    )
                ],
            ),
        }
        yield
