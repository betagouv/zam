"""Add teams back

Revision ID: 0a44e476eabc
Revises: d3b8033f60c4
Create Date: 2019-02-26 19:08:58.929724

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0a44e476eabc"
down_revision = "d3b8033f60c4"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "teams",
        sa.Column("pk", sa.Integer(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.PrimaryKeyConstraint("pk"),
    )
    op.create_table(
        "teams2users",
        sa.Column("team_pk", sa.Integer(), nullable=False),
        sa.Column("user_pk", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["team_pk"], ["teams.pk"]),
        sa.ForeignKeyConstraint(["user_pk"], ["users.pk"]),
        sa.PrimaryKeyConstraint("team_pk", "user_pk"),
    )


def downgrade():
    op.drop_table("teams2users")
    op.drop_table("teams")
