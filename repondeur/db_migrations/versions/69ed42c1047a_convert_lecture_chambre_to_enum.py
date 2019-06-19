"""Convert Lecture.chambre to enum

Revision ID: 69ed42c1047a
Revises: 5aae20474b04
Create Date: 2019-06-19 11:11:56.111993

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "69ed42c1047a"
down_revision = "5aae20474b04"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "lectures",
        "chambre",
        type_=sa.Enum(name="chambre"),
        postgresql_using="cast(upper(chambre) as chambre)",
    )


def downgrade():
    op.alter_column(
        "lectures",
        "chambre",
        type_=sa.Text,
        postgresql_using="lower(cast(chambre as text))",
    )
