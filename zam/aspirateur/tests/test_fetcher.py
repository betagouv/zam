import os

import responses


HERE = os.path.dirname(__file__)
SAMPLE_DATA_DIR = os.path.join(HERE, 'sample_data')


def read_sample_data(basename):
    filename = os.path.join(SAMPLE_DATA_DIR, basename)
    with open(filename, 'rb') as file_:
        return file_.read()


@responses.activate
def test_fetch_amendements():
    from zam_aspirateur.fetcher import fetch_amendements

    sample_data = read_sample_data('jeu_complet_2017-2018_63.csv')

    responses.add(
        responses.GET,
        'http://www.senat.fr/amendements/2017-2018/63/jeu_complet_2017-2018_63.csv',  # noqa
        body=sample_data,
        status=200,
    )

    items = fetch_amendements('2017-2018', 63)

    assert len(items) == 595

    assert items[0] == {
        "Alinéa": " ",
        "Au nom de ": "",
        "Auteur ": "M. FRASSA",
        "Date de dépôt ": "2017-11-13",
        "Dispositif ": "<body><p style=\"text-align: justify;\">Apr&#232;s l&#8217;article&#160;7</p><p style=\"text-align: justify;\">Ins&#233;rer un article&#160;additionnel ainsi r&#233;dig&#233;&#160;:</p><p style=\"text-align: justify;\">I.&#160;&#8211;&#160;Le code de la s&#233;curit&#233; sociale est ainsi modifi&#233;&#160;:</p><p style=\"text-align: justify;\">1&#176;&#160;L&#8217;article&#160;L.&#160;136&#8209;6 est ainsi modifi&#233;&#160;:</p><p style=\"text-align: justify;\">a) Le I&#160;bis&#160;est abrog&#233;&#160;;</p><p style=\"text-align: justify;\">b) &#192; la premi&#232;re phase du premier alin&#233;a du III, la premi&#232;re occurrence du mot&#160;: &#171;&#160;&#224;&#160;&#187; est remplac&#233;e par le mot&#160;: &#171;&#160;et&#160;&#187;&#160;;</p><p style=\"text-align: justify;\">2&#176;&#160;L&#8217;article&#160;L.&#160;136&#8209;7 est ainsi modifi&#233;&#160;:</p><p style=\"text-align: justify;\">a) Le I&#160;bis&#160;est abrog&#233;&#160;;</p><p style=\"text-align: justify;\">b) Le second alin&#233;a du VI est supprim&#233;&#160;;</p><p style=\"text-align: justify;\">3&#176;&#160;L&#8217;article&#160;L.&#160;245&#8209;14 est ainsi modifi&#233;&#160;:</p><p style=\"text-align: justify;\">a) &#192; la premi&#232;re phrase, les r&#233;f&#233;rences&#160;: &#171;&#160;aux I et II de&#160;&#187; sont remplac&#233;es par le mot&#160;: &#171;&#160;&#224;&#160;&#187;&#160;;</p><p style=\"text-align: justify;\">b) La deuxi&#232;me phrase est supprim&#233;e&#160;;</p><p style=\"text-align: justify;\">4&#176;&#160;Au premier alin&#233;a de l&#8217;article&#160;L.&#160;245&#8209;15, la deuxi&#232;me occurrence du mot&#160;: &#171;&#160;&#224;&#160;&#187; est remplac&#233;e par le mot&#160;: &#171;&#160;et&#160;&#187;.</p><p style=\"text-align: justify;\">II.&#160;&#8211;&#160;L&#8217;ordonnance n&#176;&#160;96&#8209;50 du 24&#160;janvier 1996 relative au remboursement de la dette sociale est ainsi modifi&#233;e&#160;:</p><p style=\"text-align: justify;\">1&#176;&#160;La seconde phrase du premier alin&#233;a du I de l&#8217;article&#160;15 est supprim&#233;e&#160;;</p><p style=\"text-align: justify;\">2&#176;&#160;&#192; la premi&#232;re phrase du I de l&#8217;article&#160;16, les r&#233;f&#233;rences&#160;: &#171;&#160;aux I et I&#160;bis&#160;&#187; sont remplac&#233;s par les mots&#160;: &#171;&#160;au I&#160;&#187;.</p><p style=\"text-align: justify;\">III.&#160;&#8211;&#160;1&#176;&#160;Les 1&#176;&#160;et 3&#176;&#160;du I et le 1&#176; du II s&#8217;appliquent aux revenus per&#231;us &#224; compter du 1<sup>er</sup>&#160;janvier 2012&#160;;</p><p style=\"text-align: justify;\">2&#176;&#160;Les 2&#176;&#160;et 4&#176;&#160;du I s&#8217;appliquent aux plus&#8209;values r&#233;alis&#233;es au titre des cessions intervenues &#224; compter de la date de publication de la pr&#233;sente loi&#160;;</p><p style=\"text-align: justify;\">3&#176;&#160;Le 2&#176;&#160;du II s&#8217;applique aux plus&#8209;values r&#233;alis&#233;es au titre des cessions intervenues &#224; compter du 1<sup>er</sup>&#160;janvier 2012.</p><p style=\"text-align: justify;\">IV.&#160;&#8211;&#160;La perte de recettes r&#233;sultant pour les organismes de s&#233;curit&#233; sociale des I &#224; III est compens&#233;e, &#224; due concurrence, par la cr&#233;ation d&#8217;une taxe additionnelle aux droits pr&#233;vus aux articles 575 et 575&#160;A du code g&#233;n&#233;ral des imp&#244;ts.</p></body>          ",  # noqa
        "Fiche Sénateur": "//www.senat.fr/senfic/frassa_christophe_andre08018u.html",  # noqa
        "Nature ": "Amt",
        "Numéro ": "1 rect.",
        "Objet ": "<body><p style=\"text-align: justify;\">Cet amendement vise &#224; rectifier une anomalie, celle de l&#8217;assujettissement des Fran&#231;ais &#233;tablis hors de France au paiement de la contribution sociale g&#233;n&#233;ralis&#233;e et de la contribution pour le remboursement de la dette sociale.</p><p style=\"text-align: justify;\">En effet, la loi de finances rectificatives pour 2012 a &#233;tendu les pr&#233;l&#232;vements sociaux aux revenus immobiliers (revenus fonciers et plus-values immobili&#232;res) de source fran&#231;aise per&#231;us par les personnes physiques fiscalement domicili&#233;es hors de France.</p><p style=\"text-align: justify;\">Par cette mesure, les Fran&#231;ais non-r&#233;sidents contribuent au financement des r&#233;gimes obligatoires de la s&#233;curit&#233; sociale, dont ils ne b&#233;n&#233;ficient pourtant pas dans la majorit&#233; des cas, leur protection sociale relevant soit d&#8217;un r&#233;gime volontaire de la Caisse des Fran&#231;ais de l&#8217;&#233;tranger soit d&#8217;un syst&#232;me de protection sociale de leur pays de r&#233;sidence.</p><p style=\"text-align: justify;\">Il en r&#233;sulte une double imposition pour les contribuables non-r&#233;sidents affili&#233;s &#224; un r&#233;gime de s&#233;curit&#233; sociale dans leur pays de r&#233;sidence et assujettis de fait aux pr&#233;l&#232;vements sociaux &#224; la fois en France et dans le pays o&#249; ils r&#233;sident.</p><p style=\"text-align: justify;\">Cette situation est contraire au droit de l&#8217;Union europ&#233;enne et particuli&#232;rement au R&#232;glement (CEE) n&#176; 1408/71 du Conseil, du 14 juin 1971, relatif &#224; l&#8217;application des r&#233;gimes de s&#233;curit&#233; sociale aux travailleurs salari&#233;s, aux travailleurs non-salari&#233;s et aux membres de leur famille qui se d&#233;placent &#224; l&#8217;int&#233;rieur de la Communaut&#233;, qui subordonne le paiement des cotisations sociales au b&#233;n&#233;fice du r&#233;gime obligatoire de s&#233;curit&#233; sociale.</p></body>",  # noqa
        "Sort ": "Adopté",
        "Subdivision ": "art. add. après Article 7",
        "Url amendement ": "//www.senat.fr/amendements/2017-2018/63/Amdt_1.html",  # noqa
    }


@responses.activate
def test_fetch_amendements_discussion():
    from zam_aspirateur.fetcher import fetch_amendements_discussion

    fake_data = {
        "info_generales": {
            "natureLoi": "Proposition de loi organique",
            "intituleLoi": "Qualité des études d'impact",
            "lecture": "1ère lecture",
            "tsgenhtml": "1519401742000",
            "idtxt": "103216",
            "nbAmdtsDeposes": "14",
            "nbAmdtsAExaminer": "0",
            "doslegsignet": "ppl16-610"
        },
        "Subdivisions": [
            {
                "libelle_subdivision": "Article 1er",
                "id_subdivision": "153938",
                "signet": "../../textes/2016-2017/610.html#AMELI_SUB_4__Article_1",  # noqa
                "Amendements": [
                    {
                        "idAmendement": "1109668",
                        "posder": "1",
                        "subpos": "-10",
                        "isSousAmendement": "false",
                        "idAmendementPere": "0",
                        "urlAmdt": "Amdt_COM-12.html",
                        "typeAmdt": "Amt",
                        "num": "COM-12",
                        "libelleAlinea": "",
                        "urlAuteur": "lamure_elisabeth04049k.html",
                        "auteur": "Mme LAMURE",
                        "isDiscussionCommune": "false",
                        "isDiscussionCommuneIsolee": "false",
                        "isIdentique": "false",
                        "sort": "Adopté",
                        "isAdopte": "true",
                        "isRejete": "false"
                    },
                    {
                        "idAmendement": "1109662",
                        "posder": "1",
                        "subpos": "0",
                        "isSousAmendement": "false",
                        "idAmendementPere": "0",
                        "urlAmdt": "Amdt_COM-6.html",
                        "typeAmdt": "Amt",
                        "num": "COM-6",
                        "libelleAlinea": "Suppr.",
                        "urlAuteur": "sueur_jean_pierre01028r.html",
                        "auteur": "M. SUEUR, rapporteur",
                        "isDiscussionCommune": "false",
                        "isDiscussionCommuneIsolee": "false",
                        "isIdentique": "false",
                        "sort": "Adopté",
                        "isAdopte": "true",
                        "isRejete": "false"
                    },
                    {
                        "idAmendement": "1109663",
                        "posder": "1",
                        "subpos": "20",
                        "isSousAmendement": "false",
                        "idAmendementPere": "0",
                        "urlAmdt": "Amdt_COM-7.html",
                        "typeAmdt": "Amt",
                        "num": "COM-7",
                        "libelleAlinea": "",
                        "urlAuteur": "sueur_jean_pierre01028r.html",
                        "auteur": "M. SUEUR, rapporteur",
                        "isDiscussionCommune": "false",
                        "isDiscussionCommuneIsolee": "false",
                        "isIdentique": "false",
                        "sort": "Adopté",
                        "isAdopte": "true",
                        "isRejete": "false"
                    },
                    {
                        "idAmendement": "1109664",
                        "posder": "2",
                        "subpos": "20",
                        "isSousAmendement": "false",
                        "idAmendementPere": "0",
                        "urlAmdt": "Amdt_COM-8.html",
                        "typeAmdt": "Amt",
                        "num": "COM-8",
                        "libelleAlinea": "",
                        "urlAuteur": "sueur_jean_pierre01028r.html",
                        "auteur": "M. SUEUR, rapporteur",
                        "isDiscussionCommune": "false",
                        "isDiscussionCommuneIsolee": "false",
                        "isIdentique": "false",
                        "sort": "Adopté",
                        "isAdopte": "true",
                        "isRejete": "false"
                    },
                    {
                        "idAmendement": "1109669",
                        "posder": "3",
                        "subpos": "20",
                        "isSousAmendement": "false",
                        "idAmendementPere": "0",
                        "urlAmdt": "Amdt_COM-13.html",
                        "typeAmdt": "Amt",
                        "num": "COM-13",
                        "libelleAlinea": "",
                        "urlAuteur": "lamure_elisabeth04049k.html",
                        "auteur": "Mme LAMURE",
                        "isDiscussionCommune": "false",
                        "isDiscussionCommuneIsolee": "false",
                        "isIdentique": "false",
                        "sort": "Rejeté",
                        "isAdopte": "false",
                        "isRejete": "true"
                    }
                ]
            },
            {
                "libelle_subdivision": "Article 2",
                "id_subdivision": "153939",
                "signet": "../../textes/2016-2017/610.html#AMELI_SUB_4__Article_2",  # noqa
                "Amendements": [
                    {
                        "idAmendement": "1109665",
                        "posder": "1",
                        "subpos": "0",
                        "isSousAmendement": "false",
                        "idAmendementPere": "0",
                        "urlAmdt": "Amdt_COM-9.html",
                        "typeAmdt": "Amt",
                        "num": "COM-9",
                        "libelleAlinea": "Al. 2",
                        "urlAuteur": "sueur_jean_pierre01028r.html",
                        "auteur": "M. SUEUR, rapporteur",
                        "isDiscussionCommune": "false",
                        "isDiscussionCommuneIsolee": "false",
                        "isIdentique": "false",
                        "sort": "Adopté",
                        "isAdopte": "true",
                        "isRejete": "false"
                    },
                    {
                        "idAmendement": "1109819",
                        "posder": "1",
                        "subpos": "0",
                        "isSousAmendement": "true",
                        "idAmendementPere": "1109665",
                        "urlAmdt": "Amdt_COM-15.html",
                        "typeAmdt": "S/Amt",
                        "num": "COM-15",
                        "libelleAlinea": "Al. 3",
                        "urlAuteur": "bas_philippe05008e.html",
                        "auteur": "M. BAS",
                        "isDiscussionCommune": "false",
                        "isDiscussionCommuneIsolee": "false",
                        "isIdentique": "false",
                        "sort": "Adopté",
                        "isAdopte": "true",
                        "isRejete": "false"
                    },
                    {
                        "idAmendement": "1109666",
                        "posder": "2",
                        "subpos": "0",
                        "isSousAmendement": "false",
                        "idAmendementPere": "0",
                        "urlAmdt": "Amdt_COM-10.html",
                        "typeAmdt": "Amt",
                        "num": "COM-10",
                        "libelleAlinea": "Al. 3",
                        "urlAuteur": "sueur_jean_pierre01028r.html",
                        "auteur": "M. SUEUR, rapporteur",
                        "isDiscussionCommune": "false",
                        "isDiscussionCommuneIsolee": "false",
                        "isIdentique": "false",
                        "sort": "Adopté",
                        "isAdopte": "true",
                        "isRejete": "false"
                    },
                    {
                        "idAmendement": "1109363",
                        "posder": "1",
                        "subpos": "20",
                        "isSousAmendement": "false",
                        "idAmendementPere": "0",
                        "urlAmdt": "Amdt_COM-2.html",
                        "typeAmdt": "Amt",
                        "num": "COM-2",
                        "libelleAlinea": "",
                        "urlAuteur": "grand_jean_pierre14211g.html",
                        "auteur": "M. GRAND",
                        "isDiscussionCommune": "false",
                        "isDiscussionCommuneIsolee": "false",
                        "isIdentique": "false",
                        "sort": "Rejeté",
                        "isAdopte": "false",
                        "isRejete": "true"
                    },
                    {
                        "idAmendement": "1109364",
                        "posder": "2",
                        "subpos": "20",
                        "isSousAmendement": "false",
                        "idAmendementPere": "0",
                        "urlAmdt": "Amdt_COM-3.html",
                        "typeAmdt": "Amt",
                        "num": "COM-3",
                        "libelleAlinea": "",
                        "urlAuteur": "grand_jean_pierre14211g.html",
                        "auteur": "M. GRAND",
                        "isDiscussionCommune": "false",
                        "isDiscussionCommuneIsolee": "false",
                        "isIdentique": "false",
                        "sort": "Rejeté",
                        "isAdopte": "false",
                        "isRejete": "true"
                    },
                    {
                        "idAmendement": "1109667",
                        "posder": "3",
                        "subpos": "20",
                        "isSousAmendement": "false",
                        "idAmendementPere": "0",
                        "urlAmdt": "Amdt_COM-11.html",
                        "typeAmdt": "Amt",
                        "num": "COM-11",
                        "libelleAlinea": "",
                        "urlAuteur": "sueur_jean_pierre01028r.html",
                        "auteur": "M. SUEUR, rapporteur",
                        "isDiscussionCommune": "false",
                        "isDiscussionCommuneIsolee": "false",
                        "isIdentique": "false",
                        "sort": "Adopté",
                        "isAdopte": "true",
                        "isRejete": "false"
                    },
                    {
                        "idAmendement": "1109366",
                        "posder": "4",
                        "subpos": "20",
                        "isSousAmendement": "false",
                        "idAmendementPere": "0",
                        "urlAmdt": "Amdt_COM-5.html",
                        "typeAmdt": "Amt",
                        "num": "COM-5",
                        "libelleAlinea": "",
                        "urlAuteur": "grand_jean_pierre14211g.html",
                        "auteur": "M. GRAND",
                        "isDiscussionCommune": "false",
                        "isDiscussionCommuneIsolee": "false",
                        "isIdentique": "false",
                        "sort": "Irrecevable",
                        "isAdopte": "false",
                        "isRejete": "false"
                    },
                    {
                        "idAmendement": "1109365",
                        "posder": "5",
                        "subpos": "20",
                        "isSousAmendement": "false",
                        "idAmendementPere": "0",
                        "urlAmdt": "Amdt_COM-4.html",
                        "typeAmdt": "Amt",
                        "num": "COM-4",
                        "libelleAlinea": "",
                        "urlAuteur": "grand_jean_pierre14211g.html",
                        "auteur": "M. GRAND",
                        "isDiscussionCommune": "false",
                        "isDiscussionCommuneIsolee": "false",
                        "isIdentique": "false",
                        "sort": "Irrecevable",
                        "isAdopte": "false",
                        "isRejete": "false"
                    }
                ]
            },
            {
                "libelle_subdivision":
                    "Intitulé de la proposition de loi organique",
                "id_subdivision": "153937",
                "signet": "../../textes/2016-2017/610.html#AMELI_SUB_1__Loi",
                "Amendements": [
                    {
                        "idAmendement": "1109362",
                        "posder": "1",
                        "subpos": "0",
                        "isSousAmendement": "false",
                        "idAmendementPere": "0",
                        "urlAmdt": "Amdt_COM-1.html",
                        "typeAmdt": "Amt",
                        "num": "COM-1",
                        "libelleAlinea": "",
                        "urlAuteur": "grand_jean_pierre14211g.html",
                        "auteur": "M. GRAND",
                        "isDiscussionCommune": "false",
                        "isDiscussionCommuneIsolee": "false",
                        "isIdentique": "false",
                        "sort": "Rejeté",
                        "isAdopte": "false",
                        "isRejete": "true"
                    }
                ]
            }
        ]
    }

    responses.add(
        responses.GET,
        'http://www.senat.fr/encommission/2016-2017/610/liste_discussion.json',
        json=fake_data,
        status=200,
    )

    data = fetch_amendements_discussion('2016-2017', 610, 'commission')

    assert data == fake_data
