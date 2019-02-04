"""Rename spaces to tables

Revision ID: c2b357257d2c
Revises: d9f119a18232
Create Date: 2019-02-04 13:40:31.076541

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "c2b357257d2c"
down_revision = "d9f119a18232"
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table("user_spaces", "user_tables")

    op.alter_column("amendements", "user_space_pk", new_column_name="user_table_pk")

    # Constraints cannot be renamed, so we drop and re-create
    op.drop_constraint(
        "amendements_user_space_pk_fkey", "amendements", type_="foreignkey"
    )
    op.create_foreign_key(
        "amendements_user_table_pk_fkey",
        "amendements",
        "user_tables",
        ["user_table_pk"],
        ["pk"],
    )


def downgrade():
    op.rename_table("user_tables", "user_spaces")

    op.alter_column("amendements", "user_table_pk", new_column_name="user_space_pk")

    op.drop_constraint(
        "amendements_user_table_pk_fkey", "amendements", type_="foreignkey"
    )
    op.create_foreign_key(
        "amendements_user_space_pk_fkey",
        "amendements",
        "user_spaces",
        ["user_space_pk"],
        ["pk"],
    )
