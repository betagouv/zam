from datetime import date


def test_parse_amendement_from_csv():

    from parser import parse_amendement_from_csv

    amend = {
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

    amendement = parse_amendement_from_csv(amend)

    assert amendement.num == "1 rect."
    assert amendement.date_depot == date(2017, 11, 13)


def test_parse_date():
    from parser import parse_date

    assert parse_date("2017-11-13") == date(2017, 11, 13)


def test_parse_date_empty_string():
    from parser import parse_date

    assert parse_date("") is None


class TestParseAmendementFromJSON:

    def test_parse_basic_data(self):
        from parser import parse_amendement_from_json

        amend = {
            "idAmendement": "1110174",
            "posder": "1",
            "subpos": "0",
            "isSousAmendement": "false",
            "idAmendementPere": "0",
            "urlAmdt": "Amdt_131.html",
            "typeAmdt": "Amt",
            "num": "131",
            "libelleAlinea": "",
            "urlAuteur": "bocquet_eric11040e.html",
            "auteur": "M. BOCQUET",
            "isDiscussionCommune": "true",
            "idDiscussionCommune": "110541",
            "isDiscussionCommuneIsolee": "false",
            "isIdentique": "false",
            "sort": "Rejeté",
            "isAdopte": "false",
            "isRejete": "true",
        }
        subdiv = {
            "libelle_subdivision": "Article 1er - Annexe (Stratégie nationale d'orientation de l'action publique)",  # noqa
            "isubdivision": "154182",
            "signet": "../../textes/2017-2018/330.html#AMELI_SUB_4__Article_1",
        }
        amendement = parse_amendement_from_json(amend, subdiv)

        assert amendement.article == "Article 1er - Annexe (Stratégie nationale d'orientation de l'action publique)"  # noqa
        assert amendement.alinea == ""

        assert amendement.num == "131"

        assert amendement.auteur == "M. BOCQUET"

        assert amendement.identique is False

    def test_discussion_commune(self):
        from parser import parse_amendement_from_json

        amend = {
            "idAmendement": "1110174",
            "posder": "1",
            "subpos": "0",
            "isSousAmendement": "false",
            "idAmendementPere": "0",
            "urlAmdt": "Amdt_131.html",
            "typeAmdt": "Amt",
            "num": "131",
            "libelleAlinea": "",
            "urlAuteur": "bocquet_eric11040e.html",
            "auteur": "M. BOCQUET",
            "isDiscussionCommune": "true",
            "idDiscussionCommune": "110541",
            "isDiscussionCommuneIsolee": "false",
            "isIdentique": "false",
            "sort": "Rejeté",
            "isAdopte": "false",
            "isRejete": "true",
        }
        subdiv = {
            "libelle_subdivision": "Article 1er - Annexe (Stratégie nationale d'orientation de l'action publique)",  # noqa
            "id_subdivision": "154182",
            "signet": "../../textes/2017-2018/330.html#AMELI_SUB_4__Article_1",
        }
        amendement = parse_amendement_from_json(amend, subdiv)

        assert amendement.discussion_commune == "110541"

    def test_not_discussion_commune(self):
        from parser import parse_amendement_from_json

        amend = {
            'idAmendement': '1103376',
            'posder': '1',
            'subpos': '0',
            'isSousAmendement': 'false',
            'idAmendementPere': '0',
            'urlAmdt': 'Amdt_31.html',
            'typeAmdt': 'Amt',
            'num': '31',
            'libelleAlinea': 'Al. 8',
            'urlAuteur': 'vanlerenberghe_jean_marie01034p.html',
            'auteur': 'M. VANLERENBERGHE',
            'isDiscussionCommune': 'false',
            'isDiscussionCommuneIsolee': 'false',
            'isIdentique': 'false',
            'sort': 'Adopté',
            'isAdopte': 'true',
            'isRejete': 'false',
        }

        subdiv = {
            'libelle_subdivision': 'Article 3',
        }

        amendement = parse_amendement_from_json(amend, subdiv)

        assert amendement.discussion_commune is None
