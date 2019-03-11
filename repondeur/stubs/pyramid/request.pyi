from typing import Any, Dict, Optional

from zam_repondeur.models.users import Team, User

class Request:
    def route_url(self, route_name: str, *elements: Any, **kw: Any) -> str: ...
    def route_path(self, route_name: str, *elements: Any, **kw: Any) -> str: ...
    def resource_url(self, resource: Any, *elements: Any, **kw: Any) -> str: ...
    def resource_path(self, resource: Any, *elements: Any, **kw: Any) -> str: ...
    environ: Dict[str, Any]
    remote_addr: Optional[str]
    registry: Any
    root: Any
    url: str
    path: str
    matchdict: Dict[str, str]
    session: Any
    GET: Any
    POST: Any
    params: Any
    unauthenticated_userid: Optional[str]
    team: Team
    user: User
