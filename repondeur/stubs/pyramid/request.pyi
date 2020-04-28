from typing import Any, Dict, List, Optional

from zam_repondeur.models.users import Team, User

class Request:
    def has_permission(self, permission: str, context: Any = None) -> bool: ...
    def route_url(self, route_name: str, *elements: Any, **kw: Any) -> str: ...
    def route_path(self, route_name: str, *elements: Any, **kw: Any) -> str: ...
    def resource_url(self, resource: Any, *elements: Any, **kw: Any) -> str: ...
    def resource_path(self, resource: Any, *elements: Any, **kw: Any) -> str: ...
    environ: Dict[str, Any]
    remote_addr: Optional[str]
    is_xhr: bool
    registry: Any
    root: Any
    context: Any
    url: str
    path: str
    matchdict: Dict[str, str]
    session: Any
    GET: Any
    POST: Any
    json_body: dict
    params: Any
    unauthenticated_userid: Optional[str]
    effective_principals: List[str]
    team: Team
    user: User
    view_name: str
