"""Add user spaces

Revision ID: 13c75654057a
Revises: c92b4d05aba8
Create Date: 2019-01-30 13:30:41.833254

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "13c75654057a"
down_revision = "c92b4d05aba8"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "user_spaces",
        sa.Column("pk", sa.Integer(), nullable=False),
        sa.Column("user_pk", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["user_pk"], ["users.pk"]),
        sa.PrimaryKeyConstraint("pk"),
    )
    op.add_column(
        "amendements", sa.Column("user_space_pk", sa.Integer(), nullable=True)
    )
    op.create_foreign_key(None, "amendements", "user_spaces", ["user_space_pk"], ["pk"])


def downgrade():
    op.drop_constraint(None, "amendements", type_="foreignkey")
    op.drop_column("amendements", "user_space_pk")
    op.drop_table("user_spaces")
