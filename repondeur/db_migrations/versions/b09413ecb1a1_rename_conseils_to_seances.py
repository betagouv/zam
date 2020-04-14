"""Rename conseils to seances

Revision ID: b09413ecb1a1
Revises: e39d4c9a9459
Create Date: 2020-04-14 10:02:40.581873

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "b09413ecb1a1"
down_revision = "e39d4c9a9459"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint(
        "conseils_lectures_conseil_pk_fkey", "conseils_lectures", type_="foreignkey"
    )
    op.rename_table(old_table_name="conseils", new_table_name="seances")
    op.rename_table(
        old_table_name="conseils_lectures", new_table_name="seances_lectures"
    )
    op.alter_column("seances_lectures", "conseil_pk", new_column_name="seance_pk")
    op.create_foreign_key(
        op.f("seances_lectures_seance_pk_fkey"),
        "seances_lectures",
        "seances",
        ["seance_pk"],
        ["pk"],
        onupdate="CASCADE",
        ondelete="CASCADE",
    )


def downgrade():
    op.drop_constraint(
        "seances_lectures_seance_pk_fkey", "seances_lectures", type_="foreignkey"
    )
    op.rename_table(old_table_name="seances", new_table_name="conseils")
    op.rename_table(
        old_table_name="seances_lectures", new_table_name="conseils_lectures"
    )
    op.alter_column("conseils_lectures", "seance_pk", new_column_name="conseil_pk")
    op.create_foreign_key(
        op.f("conseils_lectures_conseil_pk_fkey"),
        "conseils_lectures",
        "conseils",
        ["conseil_pk"],
        ["pk"],
        onupdate="CASCADE",
        ondelete="CASCADE",
    )
