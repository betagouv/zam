"""Add owned by team to lectures

Revision ID: b03b7f1042e3
Revises: 0a44e476eabc
Create Date: 2019-02-26 19:45:34.749231

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "b03b7f1042e3"
down_revision = "0a44e476eabc"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "lectures", sa.Column("owned_by_team_pk", sa.Integer(), nullable=True)
    )
    op.create_foreign_key(
        op.f("lectures_owned_by_team_pk_fkey"),
        "lectures",
        "teams",
        ["owned_by_team_pk"],
        ["pk"],
    )


def downgrade():
    op.drop_constraint(
        op.f("lectures_owned_by_team_pk_fkey"), "lectures", type_="foreignkey"
    )
    op.drop_column("lectures", "owned_by_team_pk")
