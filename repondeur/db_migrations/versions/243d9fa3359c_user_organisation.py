"""User organisation

Revision ID: 243d9fa3359c
Revises: b09413ecb1a1
Create Date: 2020-04-20 11:03:06.851174

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "243d9fa3359c"
down_revision = "b09413ecb1a1"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("users_chambres", "organisation")

    organisation_table = op.create_table(
        "organisations",
        sa.Column("pk", sa.Integer(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("pk"),
        sa.UniqueConstraint("name", name=op.f("organisations_name_key")),
    )

    # Fill up the table.
    op.bulk_insert(
        organisation_table,
        [
            {"name": "Gouvernement"},
            {"name": "Employeurs territoriaux"},
            {"name": "CFE-CGC"},
            {"name": "CFTC"},
            {"name": "CGT"},
            {"name": "FA-FP"},
            {"name": "FSU"},
            {"name": "UNSA"},
        ],
    )

    # Set default organisation to `Gouvernement` for existing users memberships.
    op.add_column(
        "users_chambres", sa.Column("organisation_pk", sa.Integer(), nullable=True),
    )
    op.execute(
        """
        UPDATE users_chambres SET organisation_pk=(
            SELECT pk FROM organisations WHERE name='Gouvernement'
        )
        """
    )
    op.alter_column("users_chambres", "organisation_pk", nullable=False)

    op.create_foreign_key(
        op.f("users_chambres_organisation_pk_fkey"),
        "users_chambres",
        "organisations",
        ["organisation_pk"],
        ["pk"],
    )


def downgrade():
    op.drop_constraint(
        op.f("users_chambres_organisation_pk_fkey"),
        "users_chambres",
        type_="foreignkey",
    )
    op.drop_column("users_chambres", "organisation_pk")
    op.drop_table("organisations")
    op.add_column(
        "users_chambres",
        sa.Column("organisation", sa.INTEGER(), autoincrement=False, nullable=True),
    )
