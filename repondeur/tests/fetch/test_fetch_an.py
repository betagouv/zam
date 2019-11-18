from datetime import date
from pathlib import Path
from textwrap import dedent
from unittest.mock import call, patch

import pytest
import responses
import transaction

from fetch.mock_an import setup_mock_responses
from zam_repondeur.services.fetch.missions import MissionRef

HERE = Path(__file__)
SAMPLE_DATA_DIR = HERE.parent / "sample_data"


# We need data about dossiers, texts and groups
pytestmark = pytest.mark.usefixtures("data_repository")


def read_sample_data(basename):
    return (SAMPLE_DATA_DIR / basename).read_text()


@pytest.fixture
def source():
    from zam_repondeur.services.fetch.an.amendements import AssembleeNationale

    return AssembleeNationale()


def assert_html_looks_like(value, expected):
    from textwrap import dedent
    from selectolax.parser import HTMLParser

    assert HTMLParser(value).html == HTMLParser(dedent(expected)).html


class TestFetchAndParseAll:
    @responses.activate
    def test_simple_amendements(self, lecture_an, app, source):
        from zam_repondeur.models import DBSession

        DBSession.add(lecture_an)

        with setup_mock_responses(
            lecture=lecture_an,
            liste=read_sample_data("an/269/liste.xml"),
            amendements=(
                ("177", read_sample_data("an/269/177.xml")),
                ("270", read_sample_data("an/269/270.xml")),
                ("723", read_sample_data("an/269/723.xml")),
                ("135", read_sample_data("an/269/135.xml")),
                ("192", read_sample_data("an/269/192.xml")),
            ),
        ):
            amendements, created, errored = source.fetch(lecture=lecture_an)

        assert len(amendements) == 5

        assert amendements[0].num == 177
        assert amendements[0].position == 1
        assert amendements[0].id_discussion_commune is None
        assert amendements[0].id_identique == 20386

        assert amendements[1].num == 270
        assert amendements[1].position == 2
        assert amendements[1].id_discussion_commune is None
        assert amendements[1].id_identique == 20386

        assert amendements[2].num == 723
        assert amendements[2].position == 3
        assert amendements[2].id_discussion_commune is None
        assert amendements[2].id_identique is None

        assert amendements[3].num == 135
        assert amendements[3].position == 4
        assert amendements[3].id_discussion_commune is None
        assert amendements[3].id_identique is None

        assert amendements[4].num == 192
        assert amendements[4].position == 5
        assert amendements[4].id_discussion_commune is None
        assert amendements[4].id_identique == 20439

        assert created == 5
        assert errored == []

    @responses.activate
    def test_simple_amendements_progress_status(self, lecture_an, app, source):
        from zam_repondeur.models import DBSession

        DBSession.add(lecture_an)

        # No progress status by default.
        assert lecture_an.get_fetch_progress() == {}

        with setup_mock_responses(
            lecture=lecture_an,
            liste=read_sample_data("an/269/liste.xml"),
            amendements=(
                ("177", read_sample_data("an/269/177.xml")),
                ("270", read_sample_data("an/269/270.xml")),
                ("723", read_sample_data("an/269/723.xml")),
                ("135", read_sample_data("an/269/135.xml")),
                ("192", read_sample_data("an/269/192.xml")),
            ),
        ), patch(
            "zam_repondeur.services.progress.ProgressRepository.set_fetch_progress"
        ) as mocked_set_fetch_progress:
            amendements, created, errored = source.fetch(lecture=lecture_an)
            # The progress is set for each amendement during the fetch.
            assert mocked_set_fetch_progress.call_args_list == [
                call("1", 1, 35),
                call("1", 2, 35),
                call("1", 3, 35),
                call("1", 4, 35),
                call("1", 5, 35),
            ]

        # Once the fetch is complete, the progress status is back to empty.
        assert lecture_an.get_fetch_progress() == {}

        assert len(amendements) == 5
        assert created == 5
        assert errored == []

    @responses.activate
    def test_fetch_amendements_not_in_discussion_list(self, lecture_an, app, source):
        from zam_repondeur.models import DBSession

        DBSession.add(lecture_an)

        with setup_mock_responses(
            lecture=lecture_an,
            liste=dedent(
                """\
                <?xml version="1.0" encoding="UTF-8"?>
                <amdtsParOrdreDeDiscussion bibard="4072" bibardSuffixe="" organe="AN"
                  legislature="14" titre="PLFSS 2017"
                  type="projet de loi de financement de la sécurité sociale">
                  <amendements>
                    <amendement place="Article 3" numero="177" sort="Rejeté"
                        parentNumero="" auteurLabel="M. DOOR"
                        auteurLabelFull="M. DOOR Jean-Pierre"
                        auteurGroupe="Les Républicains" alineaLabel="S" missionLabel=""
                        discussionCommune="" discussionCommuneAmdtPositon=""
                        discussionCommuneSsAmdtPositon="" discussionIdentique="20386"
                        discussionIdentiqueAmdtPositon="debut"
                        discussionIdentiqueSsAmdtPositon="" position="001/772" />
                  </amendements>
                </amdtsParOrdreDeDiscussion>
                """
            ),
            amendements=(
                ("177", read_sample_data("an/269/177.xml")),
                ("192", read_sample_data("an/269/192.xml")),
            ),
        ):
            amendements, created, errored = source.fetch(lecture=lecture_an)

        assert len(amendements) == 2

        assert amendements[0].num == 177
        assert amendements[0].position == 1
        assert amendements[0].id_discussion_commune is None
        assert amendements[0].id_identique == 20386

        assert amendements[1].num == 192
        assert amendements[1].position is None
        assert amendements[1].id_discussion_commune is None
        assert amendements[1].id_identique is None

        assert created == 2
        assert errored == []

    @responses.activate
    def test_commission(self, lecture_an, app, source):
        from zam_repondeur.models import DBSession

        DBSession.add(lecture_an)

        with setup_mock_responses(
            lecture=lecture_an,
            liste=read_sample_data("an/1408-CION-SOC/liste.xml"),
            amendements=(
                ("AS1", read_sample_data("an/1408-CION-SOC/AS1.xml")),
                ("AS2", read_sample_data("an/1408-CION-SOC/AS2.xml")),
            ),
        ):
            amendements, created, errored = source.fetch(lecture=lecture_an)

        assert len(amendements) == 2

        assert amendements[0].num == 1
        assert amendements[0].position == 1

        assert amendements[1].num == 2
        assert amendements[1].position is None

        assert created == 2
        assert errored == []

    @responses.activate
    def test_sous_amendements(
        self, app, source, dossier_plfss2018, texte_plfss2018_an_premiere_lecture
    ):
        from zam_repondeur.models import DBSession, Lecture, Phase

        with transaction.manager:
            texte_plfss2018_an_premiere_lecture.numero = 911
            lecture = Lecture.create(
                phase=Phase.PREMIERE_LECTURE,
                texte=texte_plfss2018_an_premiere_lecture,
                titre="Titre lecture",
                organe="PO717460",
                dossier=dossier_plfss2018,
            )

        DBSession.add(lecture)

        with setup_mock_responses(
            lecture=lecture,
            liste=read_sample_data("an/911/liste.xml"),
            amendements=(
                ("1", read_sample_data("an/911/1.xml")),
                ("2", read_sample_data("an/911/2.xml")),
                ("3", read_sample_data("an/911/3.xml")),
            ),
        ):
            amendements, created, errored = source.fetch(lecture=lecture)

        assert len(amendements) == 3

        assert amendements[0].num == 1
        assert amendements[0].position == 1
        assert amendements[0].id_discussion_commune == 3448
        assert amendements[0].id_identique == 8496

        assert amendements[1].num == 2
        assert amendements[1].position == 2
        assert amendements[1].id_discussion_commune is None
        assert amendements[1].id_identique is None

        assert amendements[2].num == 3
        assert amendements[2].position == 3
        assert amendements[2].id_discussion_commune is None
        assert amendements[1].id_identique is None

        for amendement in amendements[1:]:
            assert amendement.parent is amendements[0]
            assert amendement.parent_pk == amendements[0].pk

        assert created == 3
        assert errored == []

    @responses.activate
    def test_with_404(self, lecture_an, app, source):
        from zam_repondeur.models import DBSession

        DBSession.add(lecture_an)

        with setup_mock_responses(
            lecture=lecture_an,
            liste=read_sample_data("an/269/liste.xml"),
            amendements=(
                ("177", read_sample_data("an/269/177.xml")),
                # removed 270…
                ("723", read_sample_data("an/269/723.xml")),
                ("135", read_sample_data("an/269/135.xml")),
                ("192", read_sample_data("an/269/192.xml")),
            ),
        ):
            amendements, created, errored = source.fetch(lecture=lecture_an)

        assert len(amendements) == 4
        assert amendements[0].num == 177
        assert amendements[1].num == 723
        assert amendements[2].num == 135
        assert amendements[3].num == 192

        assert [amdt.position for amdt in amendements] == [1, 3, 4, 5]
        assert created == 4
        assert errored == ["270"]


class TestFetchDiscussionList:
    @responses.activate
    def test_simple_amendements(self, lecture_an, app):
        from zam_repondeur.services.fetch.an.amendements import (
            build_url,
            fetch_discussion_list,
        )

        responses.add(
            responses.GET,
            build_url(lecture_an),
            body=read_sample_data("an/269/liste.xml"),
            status=200,
        )

        derouleur = fetch_discussion_list(lecture=lecture_an)

        assert len(derouleur.discussion_items) == 5
        assert derouleur.discussion_items[0] == {
            "@alineaLabel": "S",
            "@auteurGroupe": "Les Républicains",
            "@auteurLabel": "M. DOOR",
            "@auteurLabelFull": "M. DOOR Jean-Pierre",
            "@discussionCommune": "",
            "@discussionCommuneAmdtPositon": "",
            "@discussionCommuneSsAmdtPositon": "",
            "@discussionIdentique": "20386",
            "@discussionIdentiqueAmdtPositon": "debut",
            "@discussionIdentiqueSsAmdtPositon": "",
            "@missionLabel": "",
            "@numero": "177",
            "@parentNumero": "",
            "@place": "Article 3",
            "@position": "001/772",
            "@sort": "Rejeté",
        }

    @responses.activate
    def test_only_one_amendement(self, lecture_an, app):
        from zam_repondeur.services.fetch.an.amendements import (
            build_url,
            fetch_discussion_list,
        )

        responses.add(
            responses.GET,
            build_url(lecture_an),
            body=dedent(
                """\
            <?xml version="1.0" encoding="UTF-8"?>
            <amdtsParOrdreDeDiscussion  bibard="4072"  bibardSuffixe=""  organe="AN"
              legislature="14"  titre="PLFSS 2017"
               type="projet de loi de financement de la sécurité sociale">
              <amendements>
                <amendement  place="Article 3"  numero="177"  sort="Rejeté"
                    parentNumero=""  auteurLabel="M. DOOR"
                    auteurLabelFull="M. DOOR Jean-Pierre"
                    auteurGroupe="Les Républicains"  alineaLabel="S"  missionLabel=""
                    discussionCommune=""  discussionCommuneAmdtPositon=""
                    discussionCommuneSsAmdtPositon=""  discussionIdentique="20386"
                    discussionIdentiqueAmdtPositon="debut"
                    discussionIdentiqueSsAmdtPositon=""  position="001/772"  />
              </amendements>
            </amdtsParOrdreDeDiscussion>
            """
            ),
            status=200,
        )

        derouleur = fetch_discussion_list(lecture=lecture_an)

        assert isinstance(derouleur.discussion_items, list)
        assert derouleur.discussion_items[0] == {
            "@alineaLabel": "S",
            "@auteurGroupe": "Les Républicains",
            "@auteurLabel": "M. DOOR",
            "@auteurLabelFull": "M. DOOR Jean-Pierre",
            "@discussionCommune": "",
            "@discussionCommuneAmdtPositon": "",
            "@discussionCommuneSsAmdtPositon": "",
            "@discussionIdentique": "20386",
            "@discussionIdentiqueAmdtPositon": "debut",
            "@discussionIdentiqueSsAmdtPositon": "",
            "@missionLabel": "",
            "@numero": "177",
            "@parentNumero": "",
            "@place": "Article 3",
            "@position": "001/772",
            "@sort": "Rejeté",
        }

    @responses.activate
    def test_list_not_found(self, lecture_an, app):
        from zam_repondeur.services.fetch.an.amendements import (
            build_url,
            fetch_discussion_list,
            NotFound,
        )

        responses.add(responses.GET, build_url(lecture_an), status=404)

        with pytest.raises(NotFound):
            fetch_discussion_list(lecture=lecture_an)


class TestFetchAmendement:
    @responses.activate
    def test_simple_amendement(self, lecture_an, app, source):
        from zam_repondeur.services.fetch.an.amendements import build_url
        from zam_repondeur.models.events.amendement import (
            CorpsAmendementModifie,
            ExposeAmendementModifie,
        )

        responses.add(
            responses.GET,
            build_url(lecture_an, 177),
            body=read_sample_data("an/269/177.xml"),
            status=200,
        )

        amendement, created = source.fetch_amendement(
            lecture=lecture_an, numero_prefixe="177", position=1
        )

        assert amendement.lecture == lecture_an
        assert amendement.num == 177
        assert amendement.rectif == 0
        assert amendement.auteur == "Door Jean-Pierre"
        assert amendement.matricule == "267289"
        assert amendement.date_depot is None
        assert amendement.sort == "rejeté"
        assert amendement.position == 1
        assert amendement.id_discussion_commune is None
        assert amendement.id_identique is None
        assert amendement.parent is None
        assert amendement.corps == "<p>Supprimer cet article.</p>"
        assert amendement.expose == (
            "<p>Amendement d&#8217;appel.</p>\n<p>Pour couvrir les d&#233;passements "
            "attendus de l&#8217;ONDAM pour 2016, cet article pr&#233;voit un "
            "pr&#233;l&#232;vement de 200 millions d&#8217;&#8364; sur les fonds de "
            "roulement de l&#8217;association nationale pour la formation permanente "
            "du personnel hospitalier (ANFH) et du fonds pour l&#8217;emploi "
            "hospitalier (FEH) pour financer le <span>fonds pour la modernisation des "
            "&#233;tablissements de sant&#233; publics et priv&#233;s</span>(FMESPP) "
            "en remplacement de cr&#233;dit de l&#8217;ONDAM. Il participe donc &#224; "
            "la pr&#233;sentation insinc&#232;re de la construction de l&#8217;ONDAM, "
            "d&#233;nonc&#233;e par le Comit&#233; d&#8217;alerte le 12 octobre "
            "dernier.</p>"
        )
        assert amendement.resume is None
        assert amendement.user_content.avis is None
        assert amendement.user_content.objet is None
        assert amendement.user_content.reponse is None

        assert len(amendement.events) == 2
        assert isinstance(amendement.events[0], ExposeAmendementModifie)
        assert amendement.events[0].created_at is not None
        assert amendement.events[0].user is None
        assert amendement.events[0].data["old_value"] == ""
        assert amendement.events[0].data["new_value"].startswith("<p>Amendement")
        assert amendement.events[0].render_summary() == (
            "L’exposé de l’amendement a été initialisé."
        )

        assert isinstance(amendement.events[1], CorpsAmendementModifie)
        assert amendement.events[1].created_at is not None
        assert amendement.events[1].user is None
        assert amendement.events[1].data["old_value"] == ""
        assert amendement.events[1].data["new_value"].startswith("<p>Supprimer")
        assert amendement.events[1].render_summary() == (
            "Le corps de l’amendement a été initialisé."
        )

    @responses.activate
    def test_fetch_amendement_gouvernement(self, lecture_an, source):
        from zam_repondeur.services.fetch.an.amendements import build_url

        responses.add(
            responses.GET,
            build_url(lecture_an, 723),
            body=read_sample_data("an/269/723.xml"),
            status=200,
        )

        amendement, created = source.fetch_amendement(
            lecture=lecture_an, numero_prefixe="723", position=1
        )

        assert amendement.gouvernemental is True
        assert amendement.groupe == ""

    @responses.activate
    def test_fetch_amendement_commission(self, lecture_an, source):
        from zam_repondeur.services.fetch.an.amendements import build_url

        responses.add(
            responses.GET,
            build_url(lecture_an, 135),
            body=read_sample_data("an/269/135.xml"),
            status=200,
        )

        amendement, created = source.fetch_amendement(
            lecture=lecture_an, numero_prefixe="135", position=1
        )

        assert amendement.gouvernemental is False
        assert amendement.auteur == "Bapt Gérard"
        assert amendement.groupe == ""  # amendement déposé par le rapporteur

    @responses.activate
    def test_fetch_amendement_with_mission_cp_ae_identical(self, lecture_an, source):
        from zam_repondeur.services.fetch.an.amendements import build_url

        responses.add(
            responses.GET,
            build_url(lecture_an, 494),
            body=read_sample_data("an/1255/494.xml"),
            status=200,
        )

        amendement, created = source.fetch_amendement(
            lecture=lecture_an, numero_prefixe="494", position=1
        )

        assert amendement.mission_titre == "Mission « Outre-mer »"
        assert amendement.mission_titre_court == "Outre-mer"

        assert_html_looks_like(
            amendement.corps,
            """
            <p>Modifier ainsi les autorisations d’engagement et les crédits de paiement :</p>
            <table class="credits">
                <caption>(en euros)</caption>
                <thead>
                    <tr>
                        <th>Programmes</th>
                        <th>+</th>
                        <th>-</th>
                    </tr>
                </thead>
                <tbody>
                        <tr>
                            <td>Emploi outre-mer</td>
                            <td>0</td>
                            <td>0</td>
                        </tr>
                        <tr>
                            <td>Conditions de vie outre-mer</td>
                            <td>0</td>
                            <td>30&#160;000&#160;000</td>
                        </tr>
                        <tr>
                            <td>Fonds de lutte contre les maladies vectorielles (ligne nouvelle)</td>
                            <td>30&#160;000&#160;000</td>
                            <td>0</td>
                        </tr>
                    <tr>
                        <td>Totaux</td>
                        <td>30&#160;000&#160;000</td>
                        <td>30&#160;000&#160;000</td>
                    </tr>
                    <tr>
                        <td>Solde</td>
                        <td colspan="2">0</td>
                    </tr>
                </tbody>
            </table>
            """,  # noqa
        )

    @responses.activate
    def test_fetch_amendement_with_mission_cp_ae_old(self, lecture_an, source):
        from zam_repondeur.services.fetch.an.amendements import build_url

        responses.add(
            responses.GET,
            build_url(lecture_an, 319),
            body=read_sample_data("an/2024/319.xml"),
            status=200,
        )

        amendement, created = source.fetch_amendement(
            lecture=lecture_an, numero_prefixe="319", position=1
        )

        assert amendement.mission_titre == "Mission « Action extérieure de l'État »"
        assert amendement.mission_titre_court == "Action extérieure de l'État"

        assert_html_looks_like(
            amendement.corps,
            """
            <p>Modifier ainsi les autorisations d’engagement et les crédits de paiement :</p>
            <table class="credits">
                <caption>(en euros)</caption>
                <thead>
                    <tr>
                        <th>Programmes</th>
                        <th>+</th>
                        <th>-</th>
                    </tr>
                </thead>
                <tbody>
                        <tr>
                            <td>Action de la France en Europe et dans le monde</td>
                            <td>0</td>
                            <td>0</td>
                        </tr>
                        <tr>
                            <td>Diplomatie culturelle et d'influence</td>
                            <td>0</td>
                            <td>-50&#160;000</td>
                        </tr>
                        <tr>
                            <td>Français à l'étranger et affaires consulaires</td>
                            <td>0</td>
                            <td>0</td>
                        </tr>
                    <tr>
                        <td>Totaux</td>
                        <td>0</td>
                        <td>-50&#160;000</td>
                    </tr>
                    <tr>
                        <td>Solde</td>
                        <td colspan="2">+50&#160;000</td>
                    </tr>
                </tbody>
            </table>
            """,  # noqa
        )

    @responses.activate
    def test_fetch_amendement_with_mission_cp_ae_different(self, lecture_an, source):
        from zam_repondeur.services.fetch.an.amendements import build_url

        responses.add(
            responses.GET,
            build_url(lecture_an, 1463),
            body=read_sample_data("an/1255/1463.xml"),
            status=200,
        )

        amendement, created = source.fetch_amendement(
            lecture=lecture_an, numero_prefixe="1463", position=1
        )

        assert amendement.mission_titre == "Mission « Cohésion des territoires »"
        assert amendement.mission_titre_court == "Cohésion des territoires"
        assert_html_looks_like(
            amendement.corps,
            """
            <p>I. Modifier ainsi les autorisations d’engagement :</p>
            <table class="credits">
                <caption>(en euros)</caption>
                <thead>
                    <tr>
                        <th>Programmes</th>
                        <th>+</th>
                        <th>-</th>
                    </tr>
                </thead>
                <tbody>
                        <tr>
                            <td>Hébergement, parcours vers le logement et insertion des personnes vulnérables</td>
                            <td>0</td>
                            <td>0</td>
                        </tr>
                        <tr>
                            <td>Aide à l&#39;accès au logement</td>
                            <td>0</td>
                            <td>0</td>
                        </tr>
                        <tr>
                            <td>Urbanisme, territoires et amélioration de l&#39;habitat</td>
                            <td>0</td>
                            <td>0</td>
                        </tr>
                        <tr>
                            <td>Impulsion et coordination de la politique d&#39;aménagement du territoire</td>
                            <td>0</td>
                            <td>10&#160;000&#160;000</td>
                        </tr>
                        <tr>
                            <td>Interventions territoriales de l&#39;État</td>
                            <td>0</td>
                            <td>0</td>
                        </tr>
                        <tr>
                            <td>Politique de la ville</td>
                            <td>0</td>
                            <td>0</td>
                        </tr>
                    <tr>
                        <td>Totaux</td>
                        <td>0</td>
                        <td>10&#160;000&#160;000</td>
                    </tr>
                    <tr>
                        <td>Solde</td>
                        <td colspan="2">-10&#160;000&#160;000</td>
                    </tr>
                </tbody>
            </table>
            <p>II. Modifier ainsi les crédits de paiement :</p>
            <table class="credits">
                <caption>(en euros)</caption>
                <thead>
                    <tr>
                        <th>Programmes</th>
                        <th>+</th>
                        <th>-</th>
                    </tr>
                </thead>
                <tbody>
                        <tr>
                            <td>Hébergement, parcours vers le logement et insertion des personnes vulnérables</td>
                            <td>0</td>
                            <td>0</td>
                        </tr>
                        <tr>
                            <td>Aide à l&#39;accès au logement</td>
                            <td>0</td>
                            <td>0</td>
                        </tr>
                        <tr>
                            <td>Urbanisme, territoires et amélioration de l&#39;habitat</td>
                            <td>0</td>
                            <td>0</td>
                        </tr>
                        <tr>
                            <td>Impulsion et coordination de la politique d&#39;aménagement du territoire</td>
                            <td>0</td>
                            <td>19&#160;329&#160;355</td>
                        </tr>
                        <tr>
                            <td>Interventions territoriales de l&#39;État</td>
                            <td>0</td>
                            <td>0</td>
                        </tr>
                        <tr>
                            <td>Politique de la ville</td>
                            <td>0</td>
                            <td>0</td>
                        </tr>
                    <tr>
                        <td>Totaux</td>
                        <td>0</td>
                        <td>19&#160;329&#160;355</td>
                    </tr>
                    <tr>
                        <td>Solde</td>
                        <td colspan="2">-19&#160;329&#160;355</td>
                    </tr>
                </tbody>
            </table>
            """,  # noqa
        )

    @responses.activate
    def test_fetch_amendement_with_mission_cp_only(self, lecture_an, source):
        from zam_repondeur.services.fetch.an.amendements import build_url

        responses.add(
            responses.GET,
            build_url(lecture_an, 398),
            body=read_sample_data("an/1255/398.xml"),
            status=200,
        )

        amendement, created = source.fetch_amendement(
            lecture=lecture_an, numero_prefixe="398", position=1
        )

        assert amendement.mission_titre == "Mission « Investissements d'avenir »"
        assert amendement.mission_titre_court == "Investissements d'avenir"
        assert_html_looks_like(
            amendement.corps,
            """
            <p>Modifier ainsi les crédits de paiement :</p>
            <table class="credits">
                <caption>(en euros)</caption>
                <thead>
                    <tr>
                        <th>Programmes</th>
                        <th>+</th>
                        <th>-</th>
                    </tr>
                </thead>
                <tbody>
                        <tr>
                            <td>Soutien des progrès de l&#39;enseignement et de la recherche</td>
                            <td>0</td>
                            <td>70&#160;000&#160;000</td>
                        </tr>
                        <tr>
                            <td>Valorisation de la recherche</td>
                            <td>0</td>
                            <td>206&#160;000&#160;000</td>
                        </tr>
                        <tr>
                            <td>Accélération de la modernisation des entreprises</td>
                            <td>0</td>
                            <td>0</td>
                        </tr>
                        <tr>
                            <td>Fonds dédié à la planification écologique (ligne nouvelle)</td>
                            <td>276&#160;000&#160;000</td>
                            <td>0</td>
                        </tr>
                    <tr>
                        <td>Totaux</td>
                        <td>276&#160;000&#160;000</td>
                        <td>276&#160;000&#160;000</td>
                    </tr>
                    <tr>
                        <td>Solde</td>
                        <td colspan="2">0</td>
                    </tr>
                </tbody>
            </table>
            """,  # noqa
        )

    @pytest.fixture
    def lecture_plf_2019(self, db):
        from zam_repondeur.models import (
            Chambre,
            Dossier,
            Lecture,
            Phase,
            Texte,
            TypeTexte,
        )

        dossier = Dossier.create(
            an_id="DLR5L15N36733",
            titre="Budget : loi de finances 2019",
            slug="loi-finances-2019",
        )
        texte = Texte.create(
            type_=TypeTexte.PROJET,
            chambre=Chambre.AN,
            legislature=15,
            numero=1490,
            date_depot=date(2018, 12, 12),
        )
        lecture = Lecture.create(
            phase=Phase.NOUVELLE_LECTURE,
            texte=texte,
            titre="Nouvelle lecture – Séance publique",
            organe="PO717460",
            dossier=dossier,
        )
        return lecture

    @responses.activate
    def test_fetch_amendement_with_single_programme(self, lecture_plf_2019, source):
        from zam_repondeur.services.fetch.an.amendements import build_url

        responses.add(
            responses.GET,
            build_url(lecture_plf_2019, 193),
            body=read_sample_data("an/1490/193.xml"),
            status=200,
        )

        amendement, created = source.fetch_amendement(
            lecture=lecture_plf_2019, numero_prefixe="193", position=1
        )

        assert amendement.mission_titre == "Mission « Sécurités »"
        assert amendement.mission_titre_court == "Sécurités"
        assert_html_looks_like(
            amendement.corps,
            """
            <p>Modifier ainsi les autorisations d’engagement et les crédits de paiement :</p>
            <table class="credits">
                <caption>(en euros)</caption>
                <thead>
                    <tr>
                        <th>Programmes</th>
                        <th>+</th>
                        <th>-</th>
                    </tr>
                </thead>
                <tbody>
                        <tr>
                            <td>Nouvelle ligne de programme (ligne nouvelle)</td>
                            <td>7&nbsp;000&nbsp;000</td>
                            <td>0</td>
                        </tr>
                    <tr>
                        <td>Totaux</td>
                        <td>7&nbsp;000&nbsp;000</td>
                        <td>0</td>
                    </tr>
                    <tr>
                        <td>Solde</td>
                        <td colspan="2">7&nbsp;000&nbsp;000</td>
                    </tr>
                </tbody>
            </table>
            """,  # noqa
        )

    @responses.activate
    def test_fetch_sous_amendement(self, lecture_an, app, source):
        from zam_repondeur.services.fetch.an.amendements import build_url

        responses.add(
            responses.GET,
            build_url(lecture_an, 155),
            body=read_sample_data("an/269/155.xml"),
            status=200,
        )

        responses.add(
            responses.GET,
            build_url(lecture_an, 941),
            body=read_sample_data("an/269/941.xml"),
            status=200,
        )

        amendement1, created = source.fetch_amendement(
            lecture=lecture_an, numero_prefixe="155", position=1
        )
        assert created
        amendement2, created = source.fetch_amendement(
            lecture=lecture_an, numero_prefixe="941", position=2
        )
        assert created

        assert amendement2.parent is amendement1

    @responses.activate
    def test_fetch_amendement_sort_nil(self, lecture_an, app, source):
        from zam_repondeur.services.fetch.an.amendements import build_url

        responses.add(
            responses.GET,
            build_url(lecture_an, 38),
            body=read_sample_data("an/269/38.xml"),
            status=200,
        )

        amendement, created = source.fetch_amendement(
            lecture=lecture_an, numero_prefixe="38", position=1
        )

        assert amendement.sort == ""

    @responses.activate
    def test_fetch_amendement_apres(self, lecture_an, app, source):
        from zam_repondeur.services.fetch.an.amendements import build_url

        responses.add(
            responses.GET,
            build_url(lecture_an, 192),
            body=read_sample_data("an/269/192.xml"),
            status=200,
        )

        amendement, created = source.fetch_amendement(
            lecture=lecture_an, numero_prefixe="192", position=1
        )

        assert amendement.article.type == "article"
        assert amendement.article.num == "8"
        assert amendement.article.mult == ""
        assert amendement.article.pos == "après"

    @responses.activate
    def test_fetch_amendement_not_found(self, lecture_an, app, source):
        from zam_repondeur.services.fetch.an.amendements import NotFound, build_url

        responses.add(responses.GET, build_url(lecture_an, 177), status=404)

        with pytest.raises(NotFound):
            source.fetch_amendement(
                lecture=lecture_an, numero_prefixe="177", position=1
            )

    @responses.activate
    def test_fetch_amendement_content_empty(self, lecture_an, app, source):
        from zam_repondeur.services.fetch.an.amendements import NotFound, build_url

        responses.add(responses.GET, build_url(lecture_an, 177), status=200, body="")

        with pytest.raises(NotFound):
            source.fetch_amendement(
                lecture=lecture_an, numero_prefixe="177", position=1
            )


class TestFetchAmendementAgain:
    @responses.activate
    def test_response_is_preserved(self, lecture_an, app, source):
        from zam_repondeur.services.fetch.an.amendements import build_url

        responses.add(
            responses.GET,
            build_url(lecture_an, 177),
            body=read_sample_data("an/269/177.xml"),
            status=200,
        )

        # Let's fetch a new amendement
        amendement1, created = source.fetch_amendement(
            lecture=lecture_an, numero_prefixe="177", position=1
        )
        assert created

        # Now let's add a response
        amendement1.user_content.avis = "Favorable"
        amendement1.user_content.objet = "Objet"
        amendement1.user_content.reponse = "Réponse"

        # And fetch the same amendement again
        amendement2, created = source.fetch_amendement(
            lecture=lecture_an, numero_prefixe="177", position=1
        )
        assert not created
        assert amendement2 is amendement1

        # The response has been preserved
        assert amendement2.user_content.avis == "Favorable"
        assert amendement2.user_content.objet == "Objet"
        assert amendement2.user_content.reponse == "Réponse"

    @responses.activate
    def test_sort_turn_irrecevable(self, lecture_an, app, source):
        from zam_repondeur.services.fetch.an.amendements import build_url
        from zam_repondeur.models.events.amendement import AmendementIrrecevable

        sample_data = read_sample_data("an/269/177.xml")
        responses.add(
            responses.GET, build_url(lecture_an, 177), body=sample_data, status=200
        )

        # On second call we want an irrecevable.
        responses.add(
            responses.GET,
            build_url(lecture_an, 177),
            body=sample_data.replace(
                "<sortEnSeance>Rejeté</sortEnSeance>",
                "<sortEnSeance>Irrecevable</sortEnSeance>",
            ),
            status=200,
        )

        # Let's fetch a new amendement
        amendement1, created = source.fetch_amendement(
            lecture=lecture_an, numero_prefixe="177", position=1
        )
        # And fetch the same amendement again
        amendement2, created = source.fetch_amendement(
            lecture=lecture_an, numero_prefixe="177", position=1
        )

        # An irrecevable event has been created
        assert len(amendement1.events) == 3
        assert isinstance(amendement1.events[0], AmendementIrrecevable)
        assert amendement1.events[0].created_at is not None
        assert amendement1.events[0].user is None
        assert amendement1.events[0].data["old_value"] == "rejeté"
        assert amendement1.events[0].data["new_value"] == "irrecevable"
        assert amendement1.events[0].render_summary() == (
            "L’amendement a été déclaré irrecevable par les services "
            "de l’Asssemblée nationale."
        )

    @responses.activate
    def test_sort_turn_irrecevable_transfers_to_index(
        self, lecture_an, app, source, user_david, user_david_table_an
    ):
        from zam_repondeur.services.fetch.an.amendements import build_url
        from zam_repondeur.models import DBSession
        from zam_repondeur.models.events.amendement import (
            AmendementIrrecevable,
            AmendementTransfere,
        )

        sample_data = read_sample_data("an/269/177.xml")
        responses.add(
            responses.GET, build_url(lecture_an, 177), body=sample_data, status=200
        )

        # On second call we want an irrecevable.
        responses.add(
            responses.GET,
            build_url(lecture_an, 177),
            body=sample_data.replace(
                "<sortEnSeance>Rejeté</sortEnSeance>",
                "<sortEnSeance>Irrecevable</sortEnSeance>",
            ),
            status=200,
        )

        # Let's fetch a new amendement
        amendement1, created = source.fetch_amendement(
            lecture=lecture_an, numero_prefixe="177", position=1
        )

        # Put it on a user table
        DBSession.add(user_david_table_an)
        user_david_table_an.add_amendement(amendement1)
        assert user_david_table_an.amendements == [amendement1]
        assert amendement1.location.user_table == user_david_table_an

        # Now fetch the same amendement again (now irrecevable)
        amendement2, created = source.fetch_amendement(
            lecture=lecture_an, numero_prefixe="177", position=1
        )

        # An irrecevable event has been created
        assert any(
            isinstance(event, AmendementIrrecevable) for event in amendement2.events
        )

        # An automatic transfer event has been created
        assert any(
            isinstance(event, AmendementTransfere) for event in amendement2.events
        )
        transfer_event = next(
            event
            for event in amendement2.events
            if isinstance(event, AmendementTransfere)
        )
        assert transfer_event.user is None
        assert transfer_event.data["old_value"] == "David (david@exemple.gouv.fr)"
        assert transfer_event.data["new_value"] == ""
        assert transfer_event.render_summary() == (
            "L’amendement a été remis automatiquement sur l’index."
        )

        # And the amendement is now on the index
        assert amendement2.location.user_table is None
        assert user_david_table_an.amendements == []

    @responses.activate
    def test_article_has_changed(self, lecture_an, app, source):
        from zam_repondeur.services.fetch.an.amendements import build_url

        responses.add(
            responses.GET,
            build_url(lecture_an, 177),
            body=read_sample_data("an/269/177.xml"),
            status=200,
        )

        amendement1, created = source.fetch_amendement(
            lecture=lecture_an, numero_prefixe="177", position=1
        )
        assert created

        amendement1.article = None  # let's change the article

        amendement2, created = source.fetch_amendement(
            lecture=lecture_an, numero_prefixe="177", position=2
        )
        assert not created
        assert amendement2 is amendement1

    @responses.activate
    def test_parent_has_changed(self, lecture_an, app, source):
        from zam_repondeur.services.fetch.an.amendements import build_url
        from zam_repondeur.models import DBSession

        responses.add(
            responses.GET,
            build_url(lecture_an, 155),
            body=read_sample_data("an/269/155.xml"),
            status=200,
        )

        responses.add(
            responses.GET,
            build_url(lecture_an, 941),
            body=read_sample_data("an/269/941.xml"),
            status=200,
        )

        parent1, created = source.fetch_amendement(
            lecture=lecture_an, numero_prefixe="155", position=1
        )
        assert created

        child1, created = source.fetch_amendement(
            lecture=lecture_an, numero_prefixe="941", position=2
        )
        assert created

        assert child1.parent is parent1
        assert child1.parent_pk == parent1.pk

        child1.parent = None  # let's change the parent amendement
        DBSession.flush()

        parent2, created = source.fetch_amendement(
            lecture=lecture_an, numero_prefixe="155", position=1
        )
        assert not created
        assert parent2 is parent1

        child2, created = source.fetch_amendement(
            lecture=lecture_an, numero_prefixe="941", position=2
        )
        assert not created
        assert child2 is child1

        assert child2.parent_pk == parent2.pk
        assert child2.parent is parent2


@pytest.mark.parametrize(
    "division,type_,num,mult,pos",
    [
        (
            {
                "titre": "pour un État au service d’une société de confiance.",
                "divisionDesignation": "TITRE",
                "type": "TITRE",
                "avantApres": "A",
                "divisionRattache": "TITRE",
                "articleAdditionnel": {
                    "@xsi:nil": "true",
                    "@xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                },
                "divisionAdditionnelle": {
                    "@xsi:nil": "true",
                    "@xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                },
                "urlDivisionTexteVise": "/15/textes/0575.asp#D_pour_un_Etat_au_service_dune_societe_d",  # noqa
            },
            "titre",
            "",
            "",
            "",
        )
    ],
)
def test_get_division(division, type_, num, mult, pos):
    from zam_repondeur.services.fetch.an.amendements import ANAmendementData

    amend_data = ANAmendementData({"amendement": {"division": division}})
    assert amend_data.get_division() == (type_, num, mult, pos)


@pytest.mark.parametrize(
    "text, expected",
    [("208", 0), ("CD208", 0), ("CD208 (Rect)", 1), ("CD208 (2ème Rect)", 2)],
)
def test_parse_numero_long_with_rect(text, expected):
    from zam_repondeur.services.fetch.an.amendements import ANAmendementData

    assert ANAmendementData.parse_numero_long_with_rect(text) == expected


@pytest.mark.parametrize(
    "text, expected",
    [
        (
            "Mission « Outre-mer »",
            MissionRef(titre="Mission « Outre-mer »", titre_court="Outre-mer"),
        ),
        (
            "« Avances à l'audiovisuel public »",
            MissionRef(
                titre="« Avances à l'audiovisuel public »",
                titre_court="Avances à l'audiovisuel public",
            ),
        ),
    ],
)
def test_parse_mission_visee(text, expected):
    from zam_repondeur.services.fetch.an.amendements import ANAmendementData

    assert ANAmendementData.parse_mission_visee(text) == expected
