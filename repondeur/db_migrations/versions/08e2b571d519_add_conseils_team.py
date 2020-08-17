"""Add conseils team

Revision ID: 08e2b571d519
Revises: fe0f5eb2cc56
Create Date: 2020-03-13 11:51:03.175180

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "08e2b571d519"
down_revision = "fe0f5eb2cc56"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("conseils", sa.Column("team_pk", sa.Integer(), nullable=False))
    op.create_foreign_key(
        op.f("conseils_team_pk_fkey"), "conseils", "teams", ["team_pk"], ["pk"]
    )


def downgrade():
    op.drop_constraint(op.f("conseils_team_pk_fkey"), "conseils", type_="foreignkey")
    op.drop_column("conseils", "team_pk")
