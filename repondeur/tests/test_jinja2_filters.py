import pytest
import transaction
from datetime import date

from zam_repondeur.views.jinja2_filters import group_by_day, paragriphy


@pytest.mark.parametrize(
    "input,output",
    [("", "<p></p>"), ("foo", "<p>foo</p>"), ("<p>bar</p>", "<p>bar</p>")],
)
def test_paragriphy(input, output):
    assert paragriphy(input) == output


def test_group_by_day(app, lecture_an, amendements_an, user_david):
    from zam_repondeur.models.events.amendement import ReponseAmendementModifiee

    with transaction.manager:
        ReponseAmendementModifiee.create(
            request=None,
            amendement=amendements_an[0],
            reponse="Réponse",
            user=user_david,
        )
        assert group_by_day(amendements_an[0].events) == [
            (date.today(), [amendements_an[0].events[0]])
        ]
