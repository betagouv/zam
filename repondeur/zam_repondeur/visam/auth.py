from typing import List

from pyramid.request import Request

from zam_repondeur.auth import AuthenticationPolicy

ADMINS = "group:admins"
GOUVERNEMENT = "group:gouvernement"
MEMBERS = "group:members"


class VisamAuthenticationPolicy(AuthenticationPolicy):
    def effective_principals(self, request: Request) -> List[str]:
        """Add chambre-related groups specific to Visam."""
        principals = super().effective_principals(request)
        if request.user is not None:
            if request.user.memberships:
                principals.append(MEMBERS)
                for chambre in request.user.chambres:
                    principals.append(f"chambre:{chambre.name}")
            else:
                principals.append(GOUVERNEMENT)
        return principals


class VisamRequest(Request):
    @property
    def is_admin_user(self) -> bool:
        return ADMINS in self.effective_principals

    @property
    def is_gouvernement_user(self) -> bool:
        return GOUVERNEMENT in self.effective_principals

    @property
    def is_member_user(self) -> bool:
        return MEMBERS in self.effective_principals
