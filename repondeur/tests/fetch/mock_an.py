import re
from contextlib import contextmanager

import responses


@contextmanager
def setup_mock_responses(lecture, liste, amendements):

    from zam_repondeur.services.fetch.an.amendements import build_url

    with responses.RequestsMock(assert_all_requests_are_fired=False) as mock_resp:
        # All responses are duplicated to handle the initial dry run
        # when fetching amendements. In real life, it would put URLs in cache
        # but that is not the case when we are running tests.

        # Add response for list of discussed amendements
        mock_resp.add(responses.GET, build_url(lecture), body=liste, status=200)
        mock_resp.add(responses.GET, build_url(lecture), body=liste, status=200)

        # Add responses for known amendements
        for number, data in amendements:
            mock_resp.add(
                responses.GET, build_url(lecture, number), body=data, status=200
            )
            mock_resp.add(
                responses.GET, build_url(lecture, number), body=data, status=200
            )

        # Other amendements will return a 404
        url_pattern = re.escape(build_url(lecture, "X")).replace("X", r"[A-Z]*\d+")
        mock_resp.add(responses.GET, re.compile(url_pattern), status=404)

        yield mock_resp
