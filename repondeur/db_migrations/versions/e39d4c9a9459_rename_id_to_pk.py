"""Rename id to pk

Revision ID: e39d4c9a9459
Revises: fb1d734cc205
Create Date: 2020-04-14 08:44:22.021370

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "e39d4c9a9459"
down_revision = "fb1d734cc205"
branch_labels = None
depends_on = None


def upgrade():
    # Rename conseils.id
    op.alter_column("conseils", "id", new_column_name="pk")

    # Rename conseils_lectures.conseil_id
    op.drop_constraint(
        "conseils_lectures_conseil_id_fkey", "conseils_lectures", type_="foreignkey"
    )
    op.alter_column("conseils_lectures", "conseil_id", new_column_name="conseil_pk")
    op.create_foreign_key(
        op.f("conseils_lectures_conseil_pk_fkey"),
        "conseils_lectures",
        "conseils",
        ["conseil_pk"],
        ["pk"],
        onupdate="CASCADE",
        ondelete="CASCADE",
    )


def downgrade():
    # Rename conseils_lectures.conseil_ipk
    op.drop_constraint(
        "conseils_lectures_conseil_pk_fkey", "conseils_lectures", type_="foreignkey"
    )
    op.alter_column("conseils_lectures", "conseil_pk", new_column_name="conseil_id")
    op.create_foreign_key(
        op.f("conseils_lectures_conseil_id_fkey"),
        "conseils_lectures",
        "conseils",
        ["conseil_id"],
        ["pk"],
        onupdate="CASCADE",
        ondelete="CASCADE",
    )

    # Rename conseils.pk
    op.alter_column("conseils", "pk", new_column_name="id")
