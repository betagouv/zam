"""
Test that we take account different kind of changes when importing a "liasse XML"
"""
from pathlib import Path

import pytest


# We need data about dossiers, texts and groups
pytestmark = pytest.mark.usefixtures("data_repository")


def open_liasse(filename):
    return (Path(__file__).parent.parent / "sample_data" / filename).open(mode="rb")


def test_article_changed(lecture_essoc2018_an_nouvelle_lecture_commission_fond):
    from zam_repondeur.fetch.an.liasse_xml import import_liasse_xml

    # Let's import amendements
    amendements, _ = import_liasse_xml(
        open_liasse("liasse.xml"), lecture_essoc2018_an_nouvelle_lecture_commission_fond
    )
    assert amendements[0].article.num == "2"

    # And import a liasse with a different target article
    amendements2, errors = import_liasse_xml(
        open_liasse("liasse_modified_article.xml"),
        lecture_essoc2018_an_nouvelle_lecture_commission_fond,
    )
    assert amendements[0].article.num == amendements2[0].article.num == "3"
    assert errors == []


def test_add_parent_amendement(lecture_essoc2018_an_nouvelle_lecture_commission_fond):
    from zam_repondeur.fetch.an.liasse_xml import import_liasse_xml

    # Let's import amendements without a parent
    amendements, _ = import_liasse_xml(
        open_liasse("liasse_removed_parent.xml"),
        lecture_essoc2018_an_nouvelle_lecture_commission_fond,
    )
    assert amendements[1].parent is None

    # And import a liasse without the parent
    amendements2, errors = import_liasse_xml(
        open_liasse("liasse.xml"), lecture_essoc2018_an_nouvelle_lecture_commission_fond
    )
    assert amendements[1].parent.num == amendements2[1].parent.num == 28
    assert errors == []


def test_remove_parent_amendement(
    lecture_essoc2018_an_nouvelle_lecture_commission_fond
):
    from zam_repondeur.fetch.an.liasse_xml import import_liasse_xml

    # Let's import amendements with a parent
    amendements, _ = import_liasse_xml(
        open_liasse("liasse.xml"), lecture_essoc2018_an_nouvelle_lecture_commission_fond
    )
    assert amendements[1].parent.num == 28

    # And import a liasse without the parent
    amendements2, errors = import_liasse_xml(
        open_liasse("liasse_removed_parent.xml"),
        lecture_essoc2018_an_nouvelle_lecture_commission_fond,
    )
    assert amendements[1].parent == amendements2[1].parent is None
    assert errors == []
