"""
Test that we take account different kind of changes when fetching updates from AN
"""
from pathlib import Path
from textwrap import dedent

import pytest
import responses

from fetch.mock_an import setup_mock_responses

# We need data about dossiers, texts and groups
pytestmark = pytest.mark.usefixtures("data_repository")


HERE = Path(__file__)
SAMPLE_DATA_DIR = HERE.parent / "sample_data"


def read_sample_data(basename):
    return (SAMPLE_DATA_DIR / basename).read_text()


@pytest.fixture
def source():
    from zam_repondeur.fetch.an.amendements import AssembleeNationale

    return AssembleeNationale()


@responses.activate
def test_position_changed(lecture_an, source):
    """
    The discussion order of amendements may change
    """
    from zam_repondeur.models import DBSession

    DBSession.add(lecture_an)

    with setup_mock_responses(
        lecture=lecture_an,
        liste=dedent(
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
                <amendement  place="Article 3"  numero="270"  sort="Rejeté"
                    parentNumero=""  auteurLabel="M. ACCOYER"
                    auteurLabelFull="M. ACCOYER Bernard"
                    auteurGroupe="Les Républicains"  alineaLabel="S"  missionLabel=""
                    discussionCommune=""  discussionCommuneAmdtPositon=""
                    discussionCommuneSsAmdtPositon=""  discussionIdentique="20386"
                    discussionIdentiqueAmdtPositon="milieu"
                    discussionIdentiqueSsAmdtPositon=""  position="002/772"  />
              </amendements>
            </amdtsParOrdreDeDiscussion>
            """
        ),
        amendements=(
            ("177", read_sample_data("an/269/177.xml")),
            ("270", read_sample_data("an/269/270.xml")),
        ),
    ):
        source.fetch(lecture=lecture_an)

    assert [amdt.num for amdt in lecture_an.amendements] == [177, 270]
    assert [amdt.position for amdt in lecture_an.amendements] == [1, 2]

    with setup_mock_responses(
        lecture=lecture_an,
        liste=dedent(
            """\
            <?xml version="1.0" encoding="UTF-8"?>
            <amdtsParOrdreDeDiscussion  bibard="4072"  bibardSuffixe=""  organe="AN"
              legislature="14"  titre="PLFSS 2017"
               type="projet de loi de financement de la sécurité sociale">
              <amendements>
                <amendement  place="Article 3"  numero="270"  sort="Rejeté"
                    parentNumero=""  auteurLabel="M. ACCOYER"
                    auteurLabelFull="M. ACCOYER Bernard"
                    auteurGroupe="Les Républicains"  alineaLabel="S"  missionLabel=""
                    discussionCommune=""  discussionCommuneAmdtPositon=""
                    discussionCommuneSsAmdtPositon=""  discussionIdentique="20386"
                    discussionIdentiqueAmdtPositon="milieu"
                    discussionIdentiqueSsAmdtPositon=""  position="001/772"  />
                <amendement  place="Article 3"  numero="177"  sort="Rejeté"
                    parentNumero=""  auteurLabel="M. DOOR"
                    auteurLabelFull="M. DOOR Jean-Pierre"
                    auteurGroupe="Les Républicains"  alineaLabel="S"  missionLabel=""
                    discussionCommune=""  discussionCommuneAmdtPositon=""
                    discussionCommuneSsAmdtPositon=""  discussionIdentique="20386"
                    discussionIdentiqueAmdtPositon="debut"
                    discussionIdentiqueSsAmdtPositon=""  position="002/772"  />
              </amendements>
            </amdtsParOrdreDeDiscussion>
            """
        ),
        amendements=(
            ("177", read_sample_data("an/269/177.xml")),
            ("270", read_sample_data("an/269/270.xml")),
        ),
    ):
        source.fetch(lecture=lecture_an)

    assert [amdt.num for amdt in lecture_an.amendements] == [177, 270]
    assert [amdt.position for amdt in lecture_an.amendements] == [2, 1]


@responses.activate
def test_abandoned_before_seance(lecture_an, source):
    """
    An amendement that is either withdrawn by its author or declared invalid
    will be removed from the list
    """
    from zam_repondeur.models import DBSession

    DBSession.add(lecture_an)

    with setup_mock_responses(
        lecture=lecture_an,
        liste=dedent(
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
                <amendement  place="Article 3"  numero="270"  sort="Rejeté"
                    parentNumero=""  auteurLabel="M. ACCOYER"
                    auteurLabelFull="M. ACCOYER Bernard"
                    auteurGroupe="Les Républicains"  alineaLabel="S"  missionLabel=""
                    discussionCommune=""  discussionCommuneAmdtPositon=""
                    discussionCommuneSsAmdtPositon=""  discussionIdentique="20386"
                    discussionIdentiqueAmdtPositon="milieu"
                    discussionIdentiqueSsAmdtPositon=""  position="002/772"  />
              </amendements>
            </amdtsParOrdreDeDiscussion>
            """
        ),
        amendements=(
            ("177", read_sample_data("an/269/177.xml")),
            ("270", read_sample_data("an/269/270.xml")),
        ),
    ):
        source.fetch(lecture=lecture_an)

    assert [amdt.num for amdt in lecture_an.amendements] == [177, 270]
    assert [amdt.position for amdt in lecture_an.amendements] == [1, 2]

    with setup_mock_responses(
        lecture=lecture_an,
        liste=dedent(
            """\
            <?xml version="1.0" encoding="UTF-8"?>
            <amdtsParOrdreDeDiscussion  bibard="4072"  bibardSuffixe=""  organe="AN"
              legislature="14"  titre="PLFSS 2017"
               type="projet de loi de financement de la sécurité sociale">
              <amendements>
                <amendement  place="Article 3"  numero="270"  sort="Rejeté"
                    parentNumero=""  auteurLabel="M. ACCOYER"
                    auteurLabelFull="M. ACCOYER Bernard"
                    auteurGroupe="Les Républicains"  alineaLabel="S"  missionLabel=""
                    discussionCommune=""  discussionCommuneAmdtPositon=""
                    discussionCommuneSsAmdtPositon=""  discussionIdentique="20386"
                    discussionIdentiqueAmdtPositon="milieu"
                    discussionIdentiqueSsAmdtPositon=""  position="002/772"  />
              </amendements>
            </amdtsParOrdreDeDiscussion>
            """
        ),
        amendements=(
            ("177", read_sample_data("an/269/177.xml")),
            ("270", read_sample_data("an/269/270.xml")),
        ),
    ):
        source.fetch(lecture=lecture_an)

    assert [amdt.num for amdt in lecture_an.amendements] == [177, 270]
    assert [amdt.position for amdt in lecture_an.amendements] == [None, 1]


@responses.activate
def test_article_changed(lecture_an, source):
    """
    The targeted article may change
    """
    from zam_repondeur.models import DBSession, Amendement

    DBSession.add(lecture_an)

    # Initial fetch
    with setup_mock_responses(
        lecture=lecture_an,
        liste=dedent(
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
                <amendement  place="Article 3"  numero="270"  sort="Rejeté"
                    parentNumero=""  auteurLabel="M. ACCOYER"
                    auteurLabelFull="M. ACCOYER Bernard"
                    auteurGroupe="Les Républicains"  alineaLabel="S"  missionLabel=""
                    discussionCommune=""  discussionCommuneAmdtPositon=""
                    discussionCommuneSsAmdtPositon=""  discussionIdentique="20386"
                    discussionIdentiqueAmdtPositon="milieu"
                    discussionIdentiqueSsAmdtPositon=""  position="002/772"  />
              </amendements>
            </amdtsParOrdreDeDiscussion>
            """
        ),
        amendements=(
            ("177", read_sample_data("an/269/177.xml")),
            ("270", read_sample_data("an/269/270.xml")),
        ),
    ):
        source.fetch(lecture=lecture_an)

    amendement = DBSession.query(Amendement).filter(Amendement.num == 177).one()
    assert str(amendement.article) == "Art. 3"

    # Fetch updates
    with setup_mock_responses(
        lecture=lecture_an,
        liste=dedent(
            """\
            <?xml version="1.0" encoding="UTF-8"?>
            <amdtsParOrdreDeDiscussion  bibard="4072"  bibardSuffixe=""  organe="AN"
              legislature="14"  titre="PLFSS 2017"
               type="projet de loi de financement de la sécurité sociale">
              <amendements>
                <amendement  place="Article 4"  numero="177"  sort="Rejeté"
                    parentNumero=""  auteurLabel="M. DOOR"
                    auteurLabelFull="M. DOOR Jean-Pierre"
                    auteurGroupe="Les Républicains"  alineaLabel="S"  missionLabel=""
                    discussionCommune=""  discussionCommuneAmdtPositon=""
                    discussionCommuneSsAmdtPositon=""  discussionIdentique="20386"
                    discussionIdentiqueAmdtPositon="debut"
                    discussionIdentiqueSsAmdtPositon=""  position="001/772"  />
                <amendement  place="Article 3"  numero="270"  sort="Rejeté"
                    parentNumero=""  auteurLabel="M. ACCOYER"
                    auteurLabelFull="M. ACCOYER Bernard"
                    auteurGroupe="Les Républicains"  alineaLabel="S"  missionLabel=""
                    discussionCommune=""  discussionCommuneAmdtPositon=""
                    discussionCommuneSsAmdtPositon=""  discussionIdentique="20386"
                    discussionIdentiqueAmdtPositon="milieu"
                    discussionIdentiqueSsAmdtPositon=""  position="002/772"  />
              </amendements>
            </amdtsParOrdreDeDiscussion>
            """
        ),
        amendements=(
            (
                "177",
                read_sample_data("an/269/177.xml").replace(
                    """\
    <division>
        <titre>Article 3</titre>
        <divisionDesignation>ART. 3</divisionDesignation>
        <type>ARTICLE</type>
        <avantApres>A</avantApres>
        <divisionRattache>ARTICLE 3</divisionRattache>
        <articleAdditionnel>0</articleAdditionnel>
        <divisionAdditionnelle>0</divisionAdditionnelle>
        <urlDivisionTexteVise>/14/textes/4072.asp#D_Article_3</urlDivisionTexteVise>
    </division>""",
                    """\
    <division>
        <titre>Article 4</titre>
        <divisionDesignation>ART. 4</divisionDesignation>
        <type>ARTICLE</type>
        <avantApres>A</avantApres>
        <divisionRattache>ARTICLE 4</divisionRattache>
        <articleAdditionnel>0</articleAdditionnel>
        <divisionAdditionnelle>0</divisionAdditionnelle>
        <urlDivisionTexteVise>/14/textes/4072.asp#D_Article_4</urlDivisionTexteVise>
    </division>""",
                ),
            ),
            ("270", read_sample_data("an/269/270.xml")),
        ),
    ):
        source.fetch(lecture=lecture_an)

    amendement = DBSession.query(Amendement).filter(Amendement.num == 177).one()
    assert str(amendement.article) == "Art. 4"


@responses.activate
def test_add_parent_amendement(lecture_an, source):
    """
    A standalone amendement can become a « sous-amendement »
    """
    from zam_repondeur.models import DBSession, Amendement

    DBSession.add(lecture_an)

    # Initial fetch
    with setup_mock_responses(
        lecture=lecture_an,
        liste=dedent(
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
                <amendement  place="Article 3"  numero="270"  sort="Rejeté"
                    parentNumero=""  auteurLabel="M. ACCOYER"
                    auteurLabelFull="M. ACCOYER Bernard"
                    auteurGroupe="Les Républicains"  alineaLabel="S"  missionLabel=""
                    discussionCommune=""  discussionCommuneAmdtPositon=""
                    discussionCommuneSsAmdtPositon=""  discussionIdentique="20386"
                    discussionIdentiqueAmdtPositon="milieu"
                    discussionIdentiqueSsAmdtPositon=""  position="002/772"  />
              </amendements>
            </amdtsParOrdreDeDiscussion>
            """
        ),
        amendements=(
            ("177", read_sample_data("an/269/177.xml")),
            ("270", read_sample_data("an/269/270.xml")),
        ),
    ):
        source.fetch(lecture=lecture_an)

    amendement = DBSession.query(Amendement).filter(Amendement.num == 270).one()
    assert amendement.parent is None

    # Fetch updates
    with setup_mock_responses(
        lecture=lecture_an,
        liste=dedent(
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
                <amendement  place="Article 3"  numero="270"  sort="Rejeté"
                    parentNumero="177"  auteurLabel="M. ACCOYER"
                    auteurLabelFull="M. ACCOYER Bernard"
                    auteurGroupe="Les Républicains"  alineaLabel="S"  missionLabel=""
                    discussionCommune=""  discussionCommuneAmdtPositon=""
                    discussionCommuneSsAmdtPositon=""  discussionIdentique="20386"
                    discussionIdentiqueAmdtPositon="milieu"
                    discussionIdentiqueSsAmdtPositon=""  position="002/772"  />
              </amendements>
            </amdtsParOrdreDeDiscussion>
            """
        ),
        amendements=(
            ("177", read_sample_data("an/269/177.xml")),
            (
                "270",
                read_sample_data("an/269/270.xml").replace(
                    '<numeroParent xsi:nil="true" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"/>',  # noqa
                    "<numeroParent>177 (Rect)</numeroParent>",
                ),
            ),
        ),
    ):
        source.fetch(lecture=lecture_an)

    amendement = DBSession.query(Amendement).filter(Amendement.num == 270).one()
    assert amendement.parent is not None
    assert amendement.parent.num == 177


@responses.activate
def test_remove_parent_amendement(lecture_an, source):
    """
    A « sous-amendement » can become a standalone one
    """
    from zam_repondeur.models import DBSession, Amendement

    DBSession.add(lecture_an)

    # Initial fetch
    with setup_mock_responses(
        lecture=lecture_an,
        liste=dedent(
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
                <amendement  place="Article 3"  numero="270"  sort="Rejeté"
                    parentNumero="177"  auteurLabel="M. ACCOYER"
                    auteurLabelFull="M. ACCOYER Bernard"
                    auteurGroupe="Les Républicains"  alineaLabel="S"  missionLabel=""
                    discussionCommune=""  discussionCommuneAmdtPositon=""
                    discussionCommuneSsAmdtPositon=""  discussionIdentique="20386"
                    discussionIdentiqueAmdtPositon="milieu"
                    discussionIdentiqueSsAmdtPositon=""  position="002/772"  />
              </amendements>
            </amdtsParOrdreDeDiscussion>
            """
        ),
        amendements=(
            ("177", read_sample_data("an/269/177.xml")),
            (
                "270",
                read_sample_data("an/269/270.xml").replace(
                    '<numeroParent xsi:nil="true" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"/>',  # noqa
                    "<numeroParent>177 (Rect)</numeroParent>",
                ),
            ),
        ),
    ):
        source.fetch(lecture=lecture_an)

    amendement = DBSession.query(Amendement).filter(Amendement.num == 270).one()
    assert amendement.parent is not None
    assert amendement.parent.num == 177

    # Fetch updates
    with setup_mock_responses(
        lecture=lecture_an,
        liste=dedent(
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
                <amendement  place="Article 3"  numero="270"  sort="Rejeté"
                    parentNumero=""  auteurLabel="M. ACCOYER"
                    auteurLabelFull="M. ACCOYER Bernard"
                    auteurGroupe="Les Républicains"  alineaLabel="S"  missionLabel=""
                    discussionCommune=""  discussionCommuneAmdtPositon=""
                    discussionCommuneSsAmdtPositon=""  discussionIdentique="20386"
                    discussionIdentiqueAmdtPositon="milieu"
                    discussionIdentiqueSsAmdtPositon=""  position="002/772"  />
              </amendements>
            </amdtsParOrdreDeDiscussion>
            """
        ),
        amendements=(
            ("177", read_sample_data("an/269/177.xml")),
            ("270", read_sample_data("an/269/270.xml")),
        ),
    ):
        source.fetch(lecture=lecture_an)

    amendement = DBSession.query(Amendement).filter(Amendement.num == 270).one()
    assert amendement.parent is None


@responses.activate
def test_rectif(lecture_an, source):
    from zam_repondeur.models import DBSession, Amendement
    from zam_repondeur.models.events.amendement import AmendementRectifie

    DBSession.add(lecture_an)

    # Initial fetch
    with setup_mock_responses(
        lecture=lecture_an,
        liste=dedent(
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
                <amendement  place="Article 3"  numero="270"  sort="Rejeté"
                    parentNumero=""  auteurLabel="M. ACCOYER"
                    auteurLabelFull="M. ACCOYER Bernard"
                    auteurGroupe="Les Républicains"  alineaLabel="S"  missionLabel=""
                    discussionCommune=""  discussionCommuneAmdtPositon=""
                    discussionCommuneSsAmdtPositon=""  discussionIdentique="20386"
                    discussionIdentiqueAmdtPositon="milieu"
                    discussionIdentiqueSsAmdtPositon=""  position="002/772"  />
              </amendements>
            </amdtsParOrdreDeDiscussion>
            """
        ),
        amendements=(
            ("177", read_sample_data("an/269/177.xml")),
            ("270", read_sample_data("an/269/270.xml")),
        ),
    ):
        source.fetch(lecture=lecture_an)

    amendement = DBSession.query(Amendement).filter(Amendement.num == 177).one()
    assert amendement.rectif == 0

    # Fetch updates
    with setup_mock_responses(
        lecture=lecture_an,
        liste=dedent(
            """\
            <?xml version="1.0" encoding="UTF-8"?>
            <amdtsParOrdreDeDiscussion  bibard="4072"  bibardSuffixe=""  organe="AN"
              legislature="14"  titre="PLFSS 2017"
               type="projet de loi de financement de la sécurité sociale">
              <amendements>
                <amendement  place="Article 4"  numero="177"  sort="Rejeté"
                    parentNumero=""  auteurLabel="M. DOOR"
                    auteurLabelFull="M. DOOR Jean-Pierre"
                    auteurGroupe="Les Républicains"  alineaLabel="S"  missionLabel=""
                    discussionCommune=""  discussionCommuneAmdtPositon=""
                    discussionCommuneSsAmdtPositon=""  discussionIdentique="20386"
                    discussionIdentiqueAmdtPositon="debut"
                    discussionIdentiqueSsAmdtPositon=""  position="001/772"  />
                <amendement  place="Article 3"  numero="270"  sort="Rejeté"
                    parentNumero=""  auteurLabel="M. ACCOYER"
                    auteurLabelFull="M. ACCOYER Bernard"
                    auteurGroupe="Les Républicains"  alineaLabel="S"  missionLabel=""
                    discussionCommune=""  discussionCommuneAmdtPositon=""
                    discussionCommuneSsAmdtPositon=""  discussionIdentique="20386"
                    discussionIdentiqueAmdtPositon="milieu"
                    discussionIdentiqueSsAmdtPositon=""  position="002/772"  />
              </amendements>
            </amdtsParOrdreDeDiscussion>
            """
        ),
        amendements=(
            (
                "177",
                read_sample_data("an/269/177.xml").replace(
                    "<numeroLong>177</numeroLong>",
                    "<numeroLong>177 (2ème Rect)</numeroLong>",
                ),
            ),
            ("270", read_sample_data("an/269/270.xml")),
        ),
    ):
        source.fetch(lecture=lecture_an)

    amendement = DBSession.query(Amendement).filter(Amendement.num == 177).one()
    assert amendement.rectif == 2
    assert len(amendement.events) == 3
    assert isinstance(amendement.events[2], AmendementRectifie)


@responses.activate
def test_rectif_with_nil(lecture_an, source):
    from zam_repondeur.models import DBSession, Amendement
    from zam_repondeur.models.events.amendement import ExposeAmendementModifie

    DBSession.add(lecture_an)

    # Initial fetch
    with setup_mock_responses(
        lecture=lecture_an,
        liste=dedent(
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
                <amendement  place="Article 3"  numero="270"  sort="Rejeté"
                    parentNumero=""  auteurLabel="M. ACCOYER"
                    auteurLabelFull="M. ACCOYER Bernard"
                    auteurGroupe="Les Républicains"  alineaLabel="S"  missionLabel=""
                    discussionCommune=""  discussionCommuneAmdtPositon=""
                    discussionCommuneSsAmdtPositon=""  discussionIdentique="20386"
                    discussionIdentiqueAmdtPositon="milieu"
                    discussionIdentiqueSsAmdtPositon=""  position="002/772"  />
              </amendements>
            </amdtsParOrdreDeDiscussion>
            """
        ),
        amendements=(
            ("177", read_sample_data("an/269/177.xml")),
            ("270", read_sample_data("an/269/270.xml")),
        ),
    ):
        source.fetch(lecture=lecture_an)

    amendement = DBSession.query(Amendement).filter(Amendement.num == 177).one()
    assert amendement.rectif == 0

    # Fetch updates
    with setup_mock_responses(
        lecture=lecture_an,
        liste=dedent(
            """\
            <?xml version="1.0" encoding="UTF-8"?>
            <amdtsParOrdreDeDiscussion  bibard="4072"  bibardSuffixe=""  organe="AN"
              legislature="14"  titre="PLFSS 2017"
               type="projet de loi de financement de la sécurité sociale">
              <amendements>
                <amendement  place="Article 4"  numero="177"  sort="Rejeté"
                    parentNumero=""  auteurLabel="M. DOOR"
                    auteurLabelFull="M. DOOR Jean-Pierre"
                    auteurGroupe="Les Républicains"  alineaLabel="S"  missionLabel=""
                    discussionCommune=""  discussionCommuneAmdtPositon=""
                    discussionCommuneSsAmdtPositon=""  discussionIdentique="20386"
                    discussionIdentiqueAmdtPositon="debut"
                    discussionIdentiqueSsAmdtPositon=""  position="001/772"  />
                <amendement  place="Article 3"  numero="270"  sort="Rejeté"
                    parentNumero=""  auteurLabel="M. ACCOYER"
                    auteurLabelFull="M. ACCOYER Bernard"
                    auteurGroupe="Les Républicains"  alineaLabel="S"  missionLabel=""
                    discussionCommune=""  discussionCommuneAmdtPositon=""
                    discussionCommuneSsAmdtPositon=""  discussionIdentique="20386"
                    discussionIdentiqueAmdtPositon="milieu"
                    discussionIdentiqueSsAmdtPositon=""  position="002/772"  />
              </amendements>
            </amdtsParOrdreDeDiscussion>
            """
        ),
        amendements=(
            (
                "177",
                read_sample_data("an/269/177.xml").replace(
                    "<numeroLong>177</numeroLong>",
                    (
                        '<numeroLong xsi:nil="true" '
                        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"/>'
                    ),
                ),
            ),
            ("270", read_sample_data("an/269/270.xml")),
        ),
    ):
        amendements, created, errored = source.fetch(lecture=lecture_an)

    assert errored == []
    amendement = DBSession.query(Amendement).filter(Amendement.num == 177).one()
    assert amendement.rectif == 0
    # No dedicated AmendementRectifie event created.
    assert len(amendement.events) == 2
    assert isinstance(amendement.events[1], ExposeAmendementModifie)
