from typing import Optional

from more_itertools import first_true
from sqlalchemy import Column, Enum, ForeignKey, Integer
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import backref, relationship

from zam_repondeur.models.base import Base, DBSession
from zam_repondeur.models.chambre import Chambre
from zam_repondeur.models.users import User

from .organisation import Organisation


class UserMembership(Base):
    """
    Association object

    https://docs.sqlalchemy.org/en/13/orm/basic_relationships.html#association-object
    """

    __tablename__ = "users_chambres"

    user_pk = Column(
        Integer,
        ForeignKey("users.pk", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )
    user = relationship(
        User, backref=backref("memberships", cascade="all, delete-orphan")
    )

    chambre = Column(
        Enum(Chambre),
        nullable=False,
        primary_key=True,
        doc="""Le conseil concerné (par exemple: CCFP, CSFPE...).""",
    )

    organisation_pk = Column(
        Integer, ForeignKey("organisations.pk"), primary_key=True, nullable=False,
    )
    organisation: Organisation = relationship(
        Organisation, backref=backref("memberships")
    )

    @classmethod
    def create(
        cls, user: User, chambre: Chambre, organisation: Organisation
    ) -> "UserMembership":
        user_membership = cls(user=user, chambre=chambre, organisation=organisation)
        DBSession.add(user_membership)
        return user_membership


def _membership_of(self: User, chambre: Chambre) -> Optional[UserMembership]:
    return first_true(self.memberships, pred=lambda m: m.chambre == chambre)


User.membership_of = _membership_of


User.chambres = association_proxy(
    "memberships", "chambre", creator=lambda user: UserMembership(user=user)
)


User.organisations = association_proxy(
    "memberships", "organisation", creator=lambda user: UserMembership(user=user)
)


Organisation.members = association_proxy(
    "memberships", "user", creator=lambda user: UserMembership(user=user)
)
