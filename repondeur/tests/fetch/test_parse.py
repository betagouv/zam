from datetime import date

import pytest


def test_parse_from_csv(lecture_senat):

    from zam_repondeur.fetch.senat.amendements import parse_from_csv

    amend = {
        "Alinéa": " ",
        "Au nom de ": "",
        "Auteur ": "M. FRASSA",
        "Date de dépôt ": "2017-11-13",
        "Dispositif ": '<body><p style="text-align: justify;">Apr&#232;s l&#8217;article&#160;7</p><p style="text-align: justify;">Ins&#233;rer un article&#160;additionnel ainsi r&#233;dig&#233;&#160;:</p><p style="text-align: justify;">I.&#160;&#8211;&#160;Le code de la s&#233;curit&#233; sociale est ainsi modifi&#233;&#160;:</p><p style="text-align: justify;">1&#176;&#160;L&#8217;article&#160;L.&#160;136&#8209;6 est ainsi modifi&#233;&#160;:</p><p style="text-align: justify;">a) Le I&#160;bis&#160;est abrog&#233;&#160;;</p><p style="text-align: justify;">b) &#192; la premi&#232;re phase du premier alin&#233;a du III, la premi&#232;re occurrence du mot&#160;: &#171;&#160;&#224;&#160;&#187; est remplac&#233;e par le mot&#160;: &#171;&#160;et&#160;&#187;&#160;;</p><p style="text-align: justify;">2&#176;&#160;L&#8217;article&#160;L.&#160;136&#8209;7 est ainsi modifi&#233;&#160;:</p><p style="text-align: justify;">a) Le I&#160;bis&#160;est abrog&#233;&#160;;</p><p style="text-align: justify;">b) Le second alin&#233;a du VI est supprim&#233;&#160;;</p><p style="text-align: justify;">3&#176;&#160;L&#8217;article&#160;L.&#160;245&#8209;14 est ainsi modifi&#233;&#160;:</p><p style="text-align: justify;">a) &#192; la premi&#232;re phrase, les r&#233;f&#233;rences&#160;: &#171;&#160;aux I et II de&#160;&#187; sont remplac&#233;es par le mot&#160;: &#171;&#160;&#224;&#160;&#187;&#160;;</p><p style="text-align: justify;">b) La deuxi&#232;me phrase est supprim&#233;e&#160;;</p><p style="text-align: justify;">4&#176;&#160;Au premier alin&#233;a de l&#8217;article&#160;L.&#160;245&#8209;15, la deuxi&#232;me occurrence du mot&#160;: &#171;&#160;&#224;&#160;&#187; est remplac&#233;e par le mot&#160;: &#171;&#160;et&#160;&#187;.</p><p style="text-align: justify;">II.&#160;&#8211;&#160;L&#8217;ordonnance n&#176;&#160;96&#8209;50 du 24&#160;janvier 1996 relative au remboursement de la dette sociale est ainsi modifi&#233;e&#160;:</p><p style="text-align: justify;">1&#176;&#160;La seconde phrase du premier alin&#233;a du I de l&#8217;article&#160;15 est supprim&#233;e&#160;;</p><p style="text-align: justify;">2&#176;&#160;&#192; la premi&#232;re phrase du I de l&#8217;article&#160;16, les r&#233;f&#233;rences&#160;: &#171;&#160;aux I et I&#160;bis&#160;&#187; sont remplac&#233;s par les mots&#160;: &#171;&#160;au I&#160;&#187;.</p><p style="text-align: justify;">III.&#160;&#8211;&#160;1&#176;&#160;Les 1&#176;&#160;et 3&#176;&#160;du I et le 1&#176; du II s&#8217;appliquent aux revenus per&#231;us &#224; compter du 1<sup>er</sup>&#160;janvier 2012&#160;;</p><p style="text-align: justify;">2&#176;&#160;Les 2&#176;&#160;et 4&#176;&#160;du I s&#8217;appliquent aux plus&#8209;values r&#233;alis&#233;es au titre des cessions intervenues &#224; compter de la date de publication de la pr&#233;sente loi&#160;;</p><p style="text-align: justify;">3&#176;&#160;Le 2&#176;&#160;du II s&#8217;applique aux plus&#8209;values r&#233;alis&#233;es au titre des cessions intervenues &#224; compter du 1<sup>er</sup>&#160;janvier 2012.</p><p style="text-align: justify;">IV.&#160;&#8211;&#160;La perte de recettes r&#233;sultant pour les organismes de s&#233;curit&#233; sociale des I &#224; III est compens&#233;e, &#224; due concurrence, par la cr&#233;ation d&#8217;une taxe additionnelle aux droits pr&#233;vus aux articles 575 et 575&#160;A du code g&#233;n&#233;ral des imp&#244;ts.</p></body>          ',  # noqa
        "Fiche Sénateur": "//www.senat.fr/senfic/frassa_christophe_andre08018u.html",  # noqa
        "Nature ": "Amt",
        "Numéro ": "1 rect.",
        "Objet ": '<body><p style="text-align: justify;">Cet amendement vise &#224; rectifier une anomalie, celle de l&#8217;assujettissement des Fran&#231;ais &#233;tablis hors de France au paiement de la contribution sociale g&#233;n&#233;ralis&#233;e et de la contribution pour le remboursement de la dette sociale.</p><p style="text-align: justify;">En effet, la loi de finances rectificatives pour 2012 a &#233;tendu les pr&#233;l&#232;vements sociaux aux revenus immobiliers (revenus fonciers et plus-values immobili&#232;res) de source fran&#231;aise per&#231;us par les personnes physiques fiscalement domicili&#233;es hors de France.</p><p style="text-align: justify;">Par cette mesure, les Fran&#231;ais non-r&#233;sidents contribuent au financement des r&#233;gimes obligatoires de la s&#233;curit&#233; sociale, dont ils ne b&#233;n&#233;ficient pourtant pas dans la majorit&#233; des cas, leur protection sociale relevant soit d&#8217;un r&#233;gime volontaire de la Caisse des Fran&#231;ais de l&#8217;&#233;tranger soit d&#8217;un syst&#232;me de protection sociale de leur pays de r&#233;sidence.</p><p style="text-align: justify;">Il en r&#233;sulte une double imposition pour les contribuables non-r&#233;sidents affili&#233;s &#224; un r&#233;gime de s&#233;curit&#233; sociale dans leur pays de r&#233;sidence et assujettis de fait aux pr&#233;l&#232;vements sociaux &#224; la fois en France et dans le pays o&#249; ils r&#233;sident.</p><p style="text-align: justify;">Cette situation est contraire au droit de l&#8217;Union europ&#233;enne et particuli&#232;rement au R&#232;glement (CEE) n&#176; 1408/71 du Conseil, du 14 juin 1971, relatif &#224; l&#8217;application des r&#233;gimes de s&#233;curit&#233; sociale aux travailleurs salari&#233;s, aux travailleurs non-salari&#233;s et aux membres de leur famille qui se d&#233;placent &#224; l&#8217;int&#233;rieur de la Communaut&#233;, qui subordonne le paiement des cotisations sociales au b&#233;n&#233;fice du r&#233;gime obligatoire de s&#233;curit&#233; sociale.</p></body>',  # noqa
        "Sort ": "Adopté",
        "Subdivision ": "art. add. après Article 7",
        "Url amendement ": "//www.senat.fr/amendements/2017-2018/63/Amdt_1.html",  # noqa
    }

    amendement, created = parse_from_csv(amend, lecture_senat)

    assert created
    assert amendement.num == 1
    assert amendement.rectif == 1
    assert amendement.num_disp == "1 rect."
    assert amendement.date_depot == date(2017, 11, 13)
    assert amendement.sort == "Adopté"

    assert (
        amendement.dispositif
        == "<p>Après l’article 7</p><p>Insérer un article additionnel ainsi rédigé :</p><p>I. – Le code de la sécurité sociale est ainsi modifié :</p><p>1° L’article L. 136‑6 est ainsi modifié :</p><p>a) Le I bis est abrogé ;</p><p>b) À la première phase du premier alinéa du III, la première occurrence du mot : « à » est remplacée par le mot : « et » ;</p><p>2° L’article L. 136‑7 est ainsi modifié :</p><p>a) Le I bis est abrogé ;</p><p>b) Le second alinéa du VI est supprimé ;</p><p>3° L’article L. 245‑14 est ainsi modifié :</p><p>a) À la première phrase, les références : « aux I et II de » sont remplacées par le mot : « à » ;</p><p>b) La deuxième phrase est supprimée ;</p><p>4° Au premier alinéa de l’article L. 245‑15, la deuxième occurrence du mot : « à » est remplacée par le mot : « et ».</p><p>II. – L’ordonnance n° 96‑50 du 24 janvier 1996 relative au remboursement de la dette sociale est ainsi modifiée :</p><p>1° La seconde phrase du premier alinéa du I de l’article 15 est supprimée ;</p><p>2° À la première phrase du I de l’article 16, les références : « aux I et I bis » sont remplacés par les mots : « au I ».</p><p>III. – 1° Les 1° et 3° du I et le 1° du II s’appliquent aux revenus perçus à compter du 1<sup>er</sup> janvier 2012 ;</p><p>2° Les 2° et 4° du I s’appliquent aux plus‑values réalisées au titre des cessions intervenues à compter de la date de publication de la présente loi ;</p><p>3° Le 2° du II s’applique aux plus‑values réalisées au titre des cessions intervenues à compter du 1<sup>er</sup> janvier 2012.</p><p>IV. – La perte de recettes résultant pour les organismes de sécurité sociale des I à III est compensée, à due concurrence, par la création d’une taxe additionnelle aux droits prévus aux articles 575 et 575 A du code général des impôts.</p>"  # noqa
    )
    assert (
        amendement.objet
        == "<p>Cet amendement vise à rectifier une anomalie, celle de l’assujettissement des Français établis hors de France au paiement de la contribution sociale généralisée et de la contribution pour le remboursement de la dette sociale.</p><p>En effet, la loi de finances rectificatives pour 2012 a étendu les prélèvements sociaux aux revenus immobiliers (revenus fonciers et plus-values immobilières) de source française perçus par les personnes physiques fiscalement domiciliées hors de France.</p><p>Par cette mesure, les Français non-résidents contribuent au financement des régimes obligatoires de la sécurité sociale, dont ils ne bénéficient pourtant pas dans la majorité des cas, leur protection sociale relevant soit d’un régime volontaire de la Caisse des Français de l’étranger soit d’un système de protection sociale de leur pays de résidence.</p><p>Il en résulte une double imposition pour les contribuables non-résidents affiliés à un régime de sécurité sociale dans leur pays de résidence et assujettis de fait aux prélèvements sociaux à la fois en France et dans le pays où ils résident.</p><p>Cette situation est contraire au droit de l’Union européenne et particulièrement au Règlement (CEE) n° 1408/71 du Conseil, du 14 juin 1971, relatif à l’application des régimes de sécurité sociale aux travailleurs salariés, aux travailleurs non-salariés et aux membres de leur famille qui se déplacent à l’intérieur de la Communauté, qui subordonne le paiement des cotisations sociales au bénéfice du régime obligatoire de sécurité sociale.</p>"  # noqa
    )


class TestExtractMatricule:
    def test_empty_url(self):
        from zam_repondeur.fetch.senat.amendements import extract_matricule

        assert extract_matricule("") is None

    def test_malformed_url(self):
        from zam_repondeur.fetch.senat.amendements import extract_matricule

        with pytest.raises(ValueError):
            extract_matricule("$amd.getUrlAuteur()")

    def test_csv_format(self):
        from zam_repondeur.fetch.senat.amendements import extract_matricule

        url = "//www.senat.fr/senfic/frassa_christophe_andre08018u.html"
        assert extract_matricule(url) == "08018U"

    def test_json_format(self):
        from zam_repondeur.fetch.senat.amendements import extract_matricule

        url = "bocquet_eric11040e.html"
        assert extract_matricule(url) == "11040E"


class TestParseDiscussionDetails:
    def test_parse_basic_data(self):
        from zam_repondeur.fetch.senat.derouleur import parse_discussion_details

        amend = {
            "idAmendement": "1104289",
            "posder": "1",
            "subpos": "0",
            "isSousAmendement": "false",
            "idAmendementPere": "0",
            "urlAmdt": "Amdt_230.html",
            "typeAmdt": "Amt",
            "num": "230 rect.",
            "libelleAlinea": "Al. 2",
            "urlAuteur": "pellevat_cyril14237s.html",
            "auteur": "M. PELLEVAT",
            "isDiscussionCommune": "false",
            "isDiscussionCommuneIsolee": "false",
            "isIdentique": "false",
            "sort": "Rejeté",
            "isAdopte": "false",
            "isRejete": "true",
        }
        details = parse_discussion_details({}, amend, position=1)

        assert details.num == 230
        assert details.position == 1
        assert details.id_discussion_commune is None
        assert details.identique is False
        assert details.parent_num is None

    def test_discussion_commune(self):
        from zam_repondeur.fetch.senat.derouleur import parse_discussion_details

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
        details = parse_discussion_details({}, amend, position=1)

        assert details.id_discussion_commune == 110541

    def test_not_discussion_commune(self):
        from zam_repondeur.fetch.senat.derouleur import parse_discussion_details

        amend = {
            "idAmendement": "1103376",
            "posder": "1",
            "subpos": "0",
            "isSousAmendement": "false",
            "idAmendementPere": "0",
            "urlAmdt": "Amdt_31.html",
            "typeAmdt": "Amt",
            "num": "31",
            "libelleAlinea": "Al. 8",
            "urlAuteur": "vanlerenberghe_jean_marie01034p.html",
            "auteur": "M. VANLERENBERGHE",
            "isDiscussionCommune": "false",
            "isDiscussionCommuneIsolee": "false",
            "isIdentique": "false",
            "sort": "Adopté",
            "isAdopte": "true",
            "isRejete": "false",
        }

        details = parse_discussion_details({}, amend, position=1)

        assert details.id_discussion_commune is None

    def test_parse_sous_amendement(self):
        from zam_repondeur.fetch.senat.derouleur import parse_discussion_details

        amend1 = {
            "idAmendement": "1104289",
            "posder": "1",
            "subpos": "0",
            "isSousAmendement": "false",
            "idAmendementPere": "0",
            "urlAmdt": "Amdt_230.html",
            "typeAmdt": "Amt",
            "num": "230 rect.",
            "libelleAlinea": "Al. 2",
            "urlAuteur": "pellevat_cyril14237s.html",
            "auteur": "M. PELLEVAT",
            "isDiscussionCommune": "false",
            "isDiscussionCommuneIsolee": "false",
            "isIdentique": "false",
            "sort": "Rejeté",
            "isAdopte": "false",
            "isRejete": "true",
        }
        amend2 = {
            "idAmendement": "1110174",
            "posder": "1",
            "subpos": "0",
            "isSousAmendement": "true",
            "idAmendementPere": "1104289",
            "urlAmdt": "Amdt_131.html",
            "typeAmdt": "Amt",
            "num": "131 rect.",
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
        details1 = parse_discussion_details({}, amend1, position=1)
        details2 = parse_discussion_details(
            {"1104289": details1.num}, amend2, position=2
        )

        assert details2.num == 131
        assert details2.parent_num == 230
