from pyramid.request import Request
from pyramid.view import view_config

from zam_repondeur.models import Amendement, DBSession
from zam_repondeur.resources import AmendementCollection


@view_config(
    context=AmendementCollection, name="order", request_method="POST", renderer="json"
)
def update_amendements_order(context: AmendementCollection, request: Request) -> dict:
    lecture = context.parent.model()
    nums = request.json_body["order"]
    amendements = [Amendement.get(lecture, num) for num in nums]

    # Reset positions first, so that we never have two with the same position
    # (which would trigger an integrity error due to the unique constraint)
    for amendement in amendements:
        amendement.position = None
    DBSession.flush()

    for i, amendement in enumerate(amendements, start=1):
        amendement.position = i

    return {}
