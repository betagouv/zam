"""Add users and teams

Revision ID: 06e826937905
Revises: ccc17664477b
Create Date: 2019-01-09 09:08:02.482576

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "06e826937905"
down_revision = "ccc17664477b"
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
        "users",
        sa.Column("pk", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("name", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("last_login_at", sa.DateTime(), nullable=True),
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
    op.drop_table("users")
    op.drop_table("teams")
