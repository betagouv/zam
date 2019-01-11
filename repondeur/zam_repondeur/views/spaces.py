from pyramid.request import Request
from pyramid.view import view_config
from zam_repondeur.resources import SpaceResource


@view_config(context=SpaceResource, renderer="myspace.html")
def myspace(context: SpaceResource, request: Request) -> dict:
    lecture = context.lecture_resource.model()
    return {"lecture": lecture, "amendements": context.amendements(user=request.user)}
