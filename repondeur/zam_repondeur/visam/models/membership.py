from sqlalchemy import Column, Enum, ForeignKey, Integer
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import backref, relationship

from zam_repondeur.models.base import Base
from zam_repondeur.models.chambre import Chambre
from zam_repondeur.models.users import User


class UserChambreMembership(Base):
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
        User, backref=backref("_chambres", cascade="all, delete-orphan")
    )

    chambre = Column(
        Enum(Chambre),
        nullable=False,
        primary_key=True,
        doc="""
        Le conseil concerné (par exemple: CCFP, CSFPE...).
        """,
    )

    organisation = Column(Integer, doc="Organisations syndicales + autres")


User.chambres = association_proxy(
    "_chambres", "chambre", creator=lambda user: UserChambreMembership(user=user)
)
