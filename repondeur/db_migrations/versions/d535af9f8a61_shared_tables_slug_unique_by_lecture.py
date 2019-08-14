"""Shared tables slug unique by lecture

Revision ID: d535af9f8a61
Revises: 9022d8bc8ab9
Create Date: 2019-08-13 17:21:42.064343

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "d535af9f8a61"
down_revision = "9022d8bc8ab9"
branch_labels = None
depends_on = None


def upgrade():
    op.create_unique_constraint(
        op.f("shared_tables_slug_lecture_pk_key"),
        "shared_tables",
        ["slug", "lecture_pk"],
    )
    op.drop_constraint("shared_tables_slug_key", "shared_tables", type_="unique")


def downgrade():
    op.create_unique_constraint("shared_tables_slug_key", "shared_tables", ["slug"])
    op.drop_constraint(
        op.f("shared_tables_slug_lecture_pk_key"), "shared_tables", type_="unique"
    )
