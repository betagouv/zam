from datetime import date
from unittest.mock import patch

import pytest


@pytest.yield_fixture(scope="session", autouse=True)
def mock_dossiers():
    from zam_repondeur.fetch.an.dossiers.models import (
        DossierRef,
        LectureRef,
        TexteRef,
        TypeTexte,
    )
    from zam_repondeur.models.chambre import Chambre

    with patch("zam_repondeur.data.get_dossiers_legislatifs_and_textes") as m_dossiers:
        textes = {
            "PRJLANR5L15B0269": TexteRef(
                uid="PRJLANR5L15B0269",
                type_=TypeTexte.PROJET,
                chambre=Chambre.AN,
                legislature=15,
                numero=269,
                titre_long="projet de loi de financement de la sécurité sociale pour 2018",  # noqa
                titre_court="PLFSS pour 2018",
                date_depot=date(2017, 10, 11),
            ),
            "PRJLSNR5S299B0063": TexteRef(
                uid="PRJLSNR5S299B0063",
                type_=TypeTexte.PROJET,
                chambre=Chambre.SENAT,
                legislature=None,
                numero=63,
                titre_long="projet de loi de financement de la sécurité sociale pour 2018",  # noqa
                titre_court="PLFSS pour 2018",
                date_depot=date(2017, 11, 6),
            ),
            "PRJLANR5L15B0806": TexteRef(
                uid="PRJLANR5L15B0806",
                type_=TypeTexte.PROJET,
                chambre=Chambre.AN,
                legislature=15,
                numero=806,
                titre_long="projet de loi renforçant l'efficacité de l'administration pour une relation de confiance avec le public",  # noqa
                titre_court="Renforcement de l'efficacité de l'administration pour une relation de confiance avec le public",  # noqa
                date_depot=date(2018, 3, 21),
            ),
            "PRJLSNR5S319B0106": TexteRef(
                uid="PRJLSNR5S319B0106",
                type_=TypeTexte.PROJET,
                chambre=Chambre.SENAT,
                legislature=None,
                numero=106,
                titre_long="projet de loi de financement de la sécurité sociale pour 2019",  # noqa
                titre_court="PLFSS pour 2019",
                date_depot=date(2018, 11, 5),
            ),
            "PRJLANR5L15B1802": TexteRef(
                uid="PRJLANR5L15B1802",
                type_=TypeTexte.PROJET,
                chambre=Chambre.AN,
                legislature=15,
                numero=1802,
                titre_long="projet de loi de transformation de la fonction publique",  # noqa
                titre_court="Transformation de la fonction publique",
                date_depot=date(2019, 3, 27),
            ),
            "PRJLANR5L15BTC1924": TexteRef(
                uid="PRJLANR5L15BTC1924",
                type_=TypeTexte.PROJET,
                chambre=Chambre.AN,
                legislature=15,
                numero=1924,
                titre_long="projet de loi sur le projet de loi, après engagement de la procédure accélérée, de transformation de la fonction publique (n°1802).",  # noqa
                titre_court="Transformation de la fonction publique",
                date_depot=date(2019, 5, 3),
            ),
        }
        dossiers = {
            "DLR5L15N36030": DossierRef(
                uid="DLR5L15N36030",
                titre="Sécurité sociale : loi de financement 2018",
                slug="plfss-2018",
                an_url="http://www.assemblee-nationale.fr/dyn/15/dossiers/alt/plfss_2018",  # noqa
                senat_url="http://www.senat.fr/dossier-legislatif/plfss2018.html",
                lectures=[
                    LectureRef(
                        chambre=Chambre.AN,
                        titre="Première lecture – Titre lecture",
                        texte=textes["PRJLANR5L15B0269"],
                        organe="PO717460",  # séance publique
                    ),
                    LectureRef(
                        chambre=Chambre.SENAT,
                        titre="Première lecture – Titre lecture",
                        texte=textes["PRJLSNR5S299B0063"],
                        organe="PO78718",  # séance publique
                    ),
                    LectureRef(
                        chambre=Chambre.SENAT,
                        titre="Première lecture – Commission saisie au fond",
                        texte=textes["PRJLSNR5S299B0063"],
                        organe="PO211493",
                    ),
                ],
            ),
            "DLR5L15N36159": DossierRef(
                uid="DLR5L15N36159",
                titre="Fonction publique : un Etat au service d'une société de confiance",  # noqa
                slug="etat-service-societe-confiance",
                an_url="http://www.assemblee-nationale.fr/dyn/15/dossiers/alt/etat_service_societe_confiance",  # noqa
                senat_url="http://www.senat.fr/dossier-legislatif/pjl17-259.html",
                lectures=[
                    LectureRef(
                        chambre=Chambre.AN,
                        titre="Nouvelle lecture – Titre lecture",
                        texte=textes["PRJLANR5L15B0806"],
                        organe="PO744107",  # commission spéciale
                    )
                ],
            ),
            "DLR5L15N36892": DossierRef(
                uid="DLR5L15N36892",
                titre="Sécurité sociale : loi de financement 2019",
                slug="plfss-2019",
                an_url="http://www.assemblee-nationale.fr/dyn/15/dossiers/alt/plfss_2019",  # noqa
                senat_url="http://www.senat.fr/dossier-legislatif/plfss2019.html",
                lectures=[
                    LectureRef(
                        chambre=Chambre.SENAT,
                        titre="Première lecture – Titre lecture",
                        texte=textes["PRJLSNR5S319B0106"],
                        organe="PO78718",  # séance publique
                    )
                ],
            ),
            "DLR5L15N37357": DossierRef(
                uid="DLR5L15N37357",
                titre="Fonction publique : transformation de la fonction publique",
                slug="transformation-fonction-publique",
                an_url="http://www.assemblee-nationale.fr/dyn/15/dossiers/alt/transformation_fonction_publique",  # noqa
                senat_url="http://www.senat.fr/dossier-legislatif/pjl18-532.html",
                lectures=[
                    LectureRef(
                        chambre=Chambre.AN,
                        titre="Première lecture – Commission saisie au fond",
                        texte=textes["PRJLANR5L15B1802"],
                        organe="PO59051",
                        partie=None,
                    ),
                    LectureRef(
                        chambre=Chambre.AN,
                        titre="Première lecture – Séance publique",
                        texte=textes["PRJLANR5L15BTC1924"],
                        organe="PO717460",
                        partie=None,
                    ),
                    # Intentionnaly removed to check it merges with Senat scraped data.
                    # LectureRef(
                    #     chambre=Chambre.SENAT,
                    #     titre="Première lecture – Commission saisie au fond",
                    #     texte=TexteRef(
                    #         uid="PRJLSNR5S319B0532",
                    #         type_=TypeTexte.PROJET,
                    #         chambre=Chambre.SENAT,
                    #         legislature=None,
                    #         numero=532,
                    #         titre_long="projet de loi de transformation de la fonction publique",  # noqa
                    #         titre_court="Transformation de la fonction publique",
                    #         date_depot=date(2019, 5, 29),
                    #     ),
                    #     organe="PO211495",
                    #     partie=None,
                    # ),
                ],
            ),
        }
        m_dossiers.return_value = dossiers, textes
        yield
