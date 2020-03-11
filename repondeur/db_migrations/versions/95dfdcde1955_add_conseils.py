"""Add conseils

Revision ID: 95dfdcde1955
Revises: 3fe97532ba21
Create Date: 2020-03-11 15:56:00.842219

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ENUM

# revision identifiers, used by Alembic.
revision = "95dfdcde1955"
down_revision = "3fe97532ba21"
branch_labels = None
depends_on = None


formation_type = ENUM(
    "ASSEMBLEE_PLENIERE", "FORMATION_SPECIALISEE", name="formation", create_type=False
)


def upgrade():
    formation_type.create(op.get_bind(), checkfirst=False)
    op.create_table(
        "conseils",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "chambre",
            ENUM("AN", "SENAT", "CCFP", name="chambre", create_type=False),
            nullable=False,
        ),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("formation", formation_type, nullable=False,),
        sa.Column("urgence_declaree", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("conseils")
    formation_type.drop(op.get_bind(), checkfirst=False)
