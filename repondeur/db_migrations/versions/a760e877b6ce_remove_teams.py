"""Remove teams

Revision ID: a760e877b6ce
Revises: 1162a0c4fc23
Create Date: 2019-01-30 13:13:28.299848

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "a760e877b6ce"
down_revision = "1162a0c4fc23"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table("teams2users")
    op.drop_table("teams")


def downgrade():
    op.create_table(
        "teams2users",
        sa.Column("team_pk", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column("user_pk", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(
            ["team_pk"], ["teams.pk"], name="teams2users_team_pk_fkey"
        ),
        sa.ForeignKeyConstraint(
            ["user_pk"], ["users.pk"], name="teams2users_user_pk_fkey"
        ),
        sa.PrimaryKeyConstraint("team_pk", "user_pk", name="teams2users_pkey"),
    )
    op.create_table(
        "teams",
        sa.Column("pk", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("name", sa.TEXT(), autoincrement=False, nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(),
            server_default=sa.text("now()"),
            autoincrement=False,
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("pk", name="teams_pkey"),
    )
