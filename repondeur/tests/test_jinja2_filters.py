from datetime import date

import pytest
import transaction
from pyramid.testing import DummyRequest


@pytest.mark.parametrize(
    "input,output",
    [("", "<p></p>"), ("foo", "<p>foo</p>"), ("<p>bar</p>", "<p>bar</p>")],
)
def test_paragriphy(input, output):
    from zam_repondeur.views.jinja2_filters import paragriphy

    assert paragriphy(input) == output


def test_group_by_day(app, lecture_an, amendements_an, user_david):
    from zam_repondeur.models.events.amendement import ReponseAmendementModifiee
    from zam_repondeur.views.jinja2_filters import group_by_day

    with transaction.manager:
        ReponseAmendementModifiee.create(
            amendement=amendements_an[0],
            reponse="Réponse",
            request=DummyRequest(remote_addr="127.0.0.1", user=user_david),
        )
        assert group_by_day(amendements_an[0].events) == [
            (date.today(), [amendements_an[0].events[0]])
        ]
