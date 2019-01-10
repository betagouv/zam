from typing import Any

from pyramid.httpexceptions import HTTPFound
from pyramid.request import Request
from pyramid.view import view_config, view_defaults

from zam_repondeur.message import Message
from zam_repondeur.models import DBSession, Team, get_one_or_create


@view_defaults(route_name="join_team")
class JoinTeam:
    def __init__(self, request: Request) -> None:
        self.request = request
        self.next_url = self.request.params.get("source") or "/"

    @view_config(request_method="GET", renderer="join_team.html")
    def get(self) -> Any:
        teams = DBSession.query(Team).all()
        return {"teams": teams, "next_url": self.next_url}

    @view_config(request_method="POST")
    def post(self) -> Any:
        name = self.request.params["name"]
        team = DBSession.query(Team).filter_by(name=name).one()

        if team not in self.request.user.teams:
            self.request.user.teams.append(team)
            message = f"Équipe « {team.name} » rejointe avec succès."
        else:
            message = "Vous êtes déjà membre de cette équipe !"
        self.request.session.flash(Message(cls="success", text=message))

        return HTTPFound(location=self.next_url)


@view_config(route_name="add_team", request_method="POST")
def add_team(request: Request) -> Any:
    name = Team.normalize_name(request.params["name"])
    team, created = get_one_or_create(Team, name=name)

    if created:
        message = f"Équipe « {team.name} » créée avec succès."
        request.user.teams.append(team)
    else:
        if team not in request.user.teams:
            request.user.teams.append(team)
            message = f"Équipe « {team.name} » rejointe avec succès."
        else:
            message = "Vous êtes déjà membre de cette équipe !"
    request.session.flash(Message(cls="success", text=message))

    next_url = request.params.get("source") or "/"
    return HTTPFound(location=next_url)
