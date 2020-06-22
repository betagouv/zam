from datetime import date


class TestDateDepot:
    def test_date_depot_not_null(self):
        from zam_repondeur.services.fetch.an.dossiers.dossiers_legislatifs import (
            parse_texte,
        )

        texte_ref = parse_texte(
            {
                "@xmlns": "http://schemas.assemblee-nationale.fr/referentiel",
                "@xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                "@xsi:type": "texteLoi_Type",
                "auteurs": {"auteur": {"organe": {"organeRef": "PO717460"}}},
                "classification": {
                    "famille": {
                        "classe": {"code": "PRJLOI", "libelle": "Projet de loi"},
                        "depot": {
                            "code": "INITNAV",
                            "libelle": "Initiative en Navette",
                        },
                    },
                    "sousType": None,
                    "statutAdoption": "ADOPTSEANCE",
                    "type": {"code": "PRJL", "libelle": "Projet de loi"},
                },
                "coSignataires": None,
                "correction": None,
                "cycleDeVie": {
                    "chrono": {
                        "dateCreation": "2017-12-19T00:00:00.000+01:00",
                        "dateDepot": "2017-12-18T00:00:00.000+01:00",
                        "datePublication": "2017-12-29T00:00:00.000+01:00",
                        "datePublicationWeb": "2017-12-19T10:00:00.000+01:00",
                    }
                },
                "denominationStructurelle": "Projet de loi",
                "depotAmendements": {
                    "amendementsCommission": {
                        "commission": {
                            "amendable": "true",
                            "dateLimiteDepot": None,
                            "organeRef": "PO420120",
                        }
                    },
                    "amendementsSeance": {"amendable": "true", "dateLimiteDepot": None},
                },
                "divisions": None,
                "dossierRef": "DLR5L15N35846",
                "imprimerie": {
                    "DIAN": None,
                    "ISBN": None,
                    "ISSN": None,
                    "nbPage": "0",
                    "prix": None,
                },
                "indexation": None,
                "legislature": "15",
                "notice": {
                    "adoptionConforme": "false",
                    "formule": ", adopté, par l'Assemblée nationale, en nouvelle "
                    "lecture, ratifiant l'ordonnance n° 2017-48 du 19 "
                    "janvier 2017 relative à la profession de physicien "
                    "médical et l'ordonnance n° 2017-50 du 19 janvier 2017 "
                    "relative à la reconnaissance des qualifications "
                    "professionnelles dans le domaine de la santé",
                    "numNotice": "60",
                },
                "provenance": "Séance",
                "redacteur": None,
                "titres": {
                    "titrePrincipal": "projet de loi ratifiant l'ordonnance n° 2017-48 "
                    "du 19 janvier 2017 relative à la profession de "
                    "physicien médical et l'ordonnance n° 2017-50 du "
                    "19 janvier 2017 relative à la reconnaissance "
                    "des qualifications professionnelles dans le "
                    "domaine de la santé",
                    "titrePrincipalCourt": "Qualifications professionnelles dans le "
                    "domaine de la santé (ordonnances n° "
                    "2017-48 et 2017-50)",
                },
                "uid": "PRJLANR5L15BTA0060",
            }
        )
        assert texte_ref.date_depot == date(2017, 12, 18)

    def test_date_depot_null(self):
        from zam_repondeur.services.fetch.an.dossiers.dossiers_legislatifs import (
            parse_texte,
        )

        texte_ref = parse_texte(
            {
                "@xmlns": "http://schemas.assemblee-nationale.fr/referentiel",
                "@xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                "@xsi:type": "texteLoi_Type",
                "auteurs": {"auteur": {"organe": {"organeRef": "PO717460"}}},
                "classification": {
                    "famille": {
                        "classe": {"code": "PRJLOI", "libelle": "Projet de loi"},
                        "depot": {
                            "code": "INITNAV",
                            "libelle": "Initiative en Navette",
                        },
                    },
                    "sousType": None,
                    "statutAdoption": "ADOPTSEANCE",
                    "type": {"code": "PRJL", "libelle": "Projet de loi"},
                },
                "coSignataires": None,
                "correction": None,
                "cycleDeVie": {
                    "chrono": {
                        "dateCreation": "2017-12-19T00:00:00.000+01:00",
                        "dateDepot": None,
                        "datePublication": "2017-12-29T00:00:00.000+01:00",
                        "datePublicationWeb": "2017-12-19T10:00:00.000+01:00",
                    }
                },
                "denominationStructurelle": "Projet de loi",
                "depotAmendements": {
                    "amendementsCommission": {
                        "commission": {
                            "amendable": "true",
                            "dateLimiteDepot": None,
                            "organeRef": "PO420120",
                        }
                    },
                    "amendementsSeance": {"amendable": "true", "dateLimiteDepot": None},
                },
                "divisions": None,
                "dossierRef": "DLR5L15N35846",
                "imprimerie": {
                    "DIAN": None,
                    "ISBN": None,
                    "ISSN": None,
                    "nbPage": "0",
                    "prix": None,
                },
                "indexation": None,
                "legislature": "15",
                "notice": {
                    "adoptionConforme": "false",
                    "formule": ", adopté, par l'Assemblée nationale, en nouvelle "
                    "lecture, ratifiant l'ordonnance n° 2017-48 du 19 "
                    "janvier 2017 relative à la profession de physicien "
                    "médical et l'ordonnance n° 2017-50 du 19 janvier 2017 "
                    "relative à la reconnaissance des qualifications "
                    "professionnelles dans le domaine de la santé",
                    "numNotice": "60",
                },
                "provenance": "Séance",
                "redacteur": None,
                "titres": {
                    "titrePrincipal": "projet de loi ratifiant l'ordonnance n° 2017-48 "
                    "du 19 janvier 2017 relative à la profession de "
                    "physicien médical et l'ordonnance n° 2017-50 du "
                    "19 janvier 2017 relative à la reconnaissance "
                    "des qualifications professionnelles dans le "
                    "domaine de la santé",
                    "titrePrincipalCourt": "Qualifications professionnelles dans le "
                    "domaine de la santé (ordonnances n° "
                    "2017-48 et 2017-50)",
                },
                "uid": "PRJLANR5L15BTA0060",
            }
        )
        assert texte_ref.date_depot == date(2017, 12, 19)
