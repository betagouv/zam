"""Add amendement mission model

Revision ID: 75e6a7fd6a52
Revises: 69ed42c1047a
Create Date: 2019-06-20 11:04:21.406426

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "75e6a7fd6a52"
down_revision = "69ed42c1047a"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "amendement_missions",
        sa.Column("pk", sa.Integer(), nullable=False),
        sa.Column("titre", sa.Text(), nullable=True),
        sa.Column("titre_court", sa.Text(), nullable=True),
        sa.Column("amendement_pk", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["amendement_pk"],
            ["amendements.pk"],
            name=op.f("amendement_missions_amendement_pk_fkey"),
        ),
        sa.PrimaryKeyConstraint("pk"),
    )


def downgrade():
    op.drop_table("amendement_missions")
