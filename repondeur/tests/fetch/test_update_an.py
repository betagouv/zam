"""
Test that we take account different kind of changes when fetching updates from AN
"""
from pathlib import Path
from textwrap import dedent

import responses

from zam_repondeur.fetch.an.amendements import fetch_and_parse_all, build_url
from zam_repondeur.models import Amendement, DBSession


HERE = Path(__file__)
SAMPLE_DATA_DIR = HERE.parent / "sample_data"


def read_sample_data(basename):
    return (SAMPLE_DATA_DIR / basename).read_text()


@responses.activate
def test_position_changed(lecture_an):
    """
    The discussion order of amendements may change
    """

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
        status=200,
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
        status=200,
    )
    responses.add(
        responses.GET,
        build_url(lecture_an, 177),
        body=read_sample_data("an/269/177.xml"),
        status=200,
    )
    responses.add(
        responses.GET,
        build_url(lecture_an, 270),
        body=read_sample_data("an/269/270.xml"),
        status=200,
    )

    DBSession.add(lecture_an)

    fetch_and_parse_all(lecture=lecture_an)

    assert [amdt.num for amdt in lecture_an.amendements] == [177, 270]
    assert [amdt.position for amdt in lecture_an.amendements] == [1, 2]

    fetch_and_parse_all(lecture=lecture_an)

    assert [amdt.num for amdt in lecture_an.amendements] == [177, 270]
    assert [amdt.position for amdt in lecture_an.amendements] == [2, 1]


@responses.activate
def test_abandoned_before_seance(lecture_an):
    """
    An amendement that is either withdrawn by its author or declared invalid
    will be removed from the list
    """

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
        status=200,
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
    responses.add(
        responses.GET,
        build_url(lecture_an, 177),
        body=read_sample_data("an/269/177.xml"),
        status=200,
    )
    responses.add(
        responses.GET,
        build_url(lecture_an, 270),
        body=read_sample_data("an/269/270.xml"),
        status=200,
    )

    DBSession.add(lecture_an)

    fetch_and_parse_all(lecture=lecture_an)

    assert [amdt.num for amdt in lecture_an.amendements] == [177, 270]
    assert [amdt.position for amdt in lecture_an.amendements] == [1, 2]

    fetch_and_parse_all(lecture=lecture_an)

    assert [amdt.num for amdt in lecture_an.amendements] == [177, 270]
    assert [amdt.position for amdt in lecture_an.amendements] == [1, None]


@responses.activate
def test_article_changed(lecture_an):
    """
    The targeted article may change
    """

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
        status=200,
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
        status=200,
    )
    responses.add(
        responses.GET,
        build_url(lecture_an, 177),
        body=read_sample_data("an/269/177.xml"),
        status=200,
    )
    responses.add(
        responses.GET,
        build_url(lecture_an, 177),
        body=read_sample_data("an/269/177.xml").replace(
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
        status=200,
    )
    responses.add(
        responses.GET,
        build_url(lecture_an, 270),
        body=read_sample_data("an/269/270.xml"),
        status=200,
    )

    DBSession.add(lecture_an)

    # Initial fetch

    fetch_and_parse_all(lecture=lecture_an)

    amendement = DBSession.query(Amendement).filter(Amendement.num == 177).one()
    assert str(amendement.article) == "Art. 3"

    # Fetch updates

    fetch_and_parse_all(lecture=lecture_an)

    amendement = DBSession.query(Amendement).filter(Amendement.num == 177).one()
    assert str(amendement.article) == "Art. 4"


@responses.activate
def test_add_parent_amendement(lecture_an):
    """
    A standalone amendement can become a « sous-amendement »
    """

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
        status=200,
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
        status=200,
    )
    responses.add(
        responses.GET,
        build_url(lecture_an, 177),
        body=read_sample_data("an/269/177.xml"),
        status=200,
    )
    responses.add(
        responses.GET,
        build_url(lecture_an, 270),
        body=read_sample_data("an/269/270.xml"),
        status=200,
    )
    responses.add(
        responses.GET,
        build_url(lecture_an, 270),
        body=read_sample_data("an/269/270.xml").replace(
            '<numeroParent xsi:nil="true" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"/>',  # noqa
            "<numeroParent>177 (Rect)</numeroParent>",
        ),
        status=200,
    )

    DBSession.add(lecture_an)

    # Initial fetch

    fetch_and_parse_all(lecture=lecture_an)

    amendement = DBSession.query(Amendement).filter(Amendement.num == 270).one()
    assert amendement.parent is None

    # Fetch updates

    fetch_and_parse_all(lecture=lecture_an)

    amendement = DBSession.query(Amendement).filter(Amendement.num == 270).one()
    assert amendement.parent is not None
    assert amendement.parent.num == 177


@responses.activate
def test_remove_parent_amendement(lecture_an):
    """
    A « sous-amendement » can become a standalone one
    """

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
        status=200,
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
        status=200,
    )
    responses.add(
        responses.GET,
        build_url(lecture_an, 177),
        body=read_sample_data("an/269/177.xml"),
        status=200,
    )
    responses.add(
        responses.GET,
        build_url(lecture_an, 270),
        body=read_sample_data("an/269/270.xml").replace(
            '<numeroParent xsi:nil="true" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"/>',  # noqa
            "<numeroParent>177 (Rect)</numeroParent>",
        ),
        status=200,
    )
    responses.add(
        responses.GET,
        build_url(lecture_an, 270),
        body=read_sample_data("an/269/270.xml"),
        status=200,
    )

    DBSession.add(lecture_an)

    # Initial fetch

    fetch_and_parse_all(lecture=lecture_an)

    amendement = DBSession.query(Amendement).filter(Amendement.num == 270).one()
    assert amendement.parent is not None
    assert amendement.parent.num == 177

    # Fetch updates

    fetch_and_parse_all(lecture=lecture_an)

    amendement = DBSession.query(Amendement).filter(Amendement.num == 270).one()
    assert amendement.parent is None
