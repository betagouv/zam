"""Add amendement mission model

Revision ID: 851d659d6eef
Revises: 69ed42c1047a
Create Date: 2019-06-24 11:15:56.496405

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "851d659d6eef"
down_revision = "69ed42c1047a"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "missions",
        sa.Column("pk", sa.Integer(), nullable=False),
        sa.Column("titre", sa.Text(), nullable=True),
        sa.Column("titre_court", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("pk"),
    )
    op.add_column("amendements", sa.Column("mission_pk", sa.Integer(), nullable=True))
    op.create_foreign_key(
        op.f("amendements_mission_pk_fkey"),
        "amendements",
        "missions",
        ["mission_pk"],
        ["pk"],
    )


def downgrade():
    op.drop_constraint(
        op.f("amendements_mission_pk_fkey"), "amendements", type_="foreignkey"
    )
    op.drop_column("amendements", "mission_pk")
    op.drop_table("missions")
