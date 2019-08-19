"""Add user spaces

Revision ID: 13c75654057a
Revises: c92b4d05aba8
Create Date: 2019-01-30 13:30:41.833254

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "13c75654057a"
down_revision = "c92b4d05aba8"
branch_labels = None
depends_on = None


def upgrade():
    user_spaces = op.create_table(
        "user_spaces",
        sa.Column("pk", sa.Integer(), nullable=False),
        sa.Column("user_pk", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["user_pk"], ["users.pk"]),
        sa.PrimaryKeyConstraint("pk"),
    )

    connection = op.get_bind()
    users = connection.execute("SELECT pk FROM users;")
    op.bulk_insert(user_spaces, [{"user_pk": pk} for (pk,) in users])

    op.add_column(
        "amendements", sa.Column("user_space_pk", sa.Integer(), nullable=True)
    )
    op.create_foreign_key(
        "amendements_user_space_pk_fkey",
        "amendements",
        "user_spaces",
        ["user_space_pk"],
        ["pk"],
    )


def downgrade():
    op.drop_constraint(
        "amendements_user_space_pk_fkey", "amendements", type_="foreignkey"
    )
    op.drop_column("amendements", "user_space_pk")
    op.drop_table("user_spaces")
