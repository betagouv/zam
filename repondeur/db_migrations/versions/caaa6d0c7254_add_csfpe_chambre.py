"""Add CSFPE chambre

Revision ID: caaa6d0c7254
Revises: 245e371cbf82
Create Date: 2020-03-11 17:19:11.567332

"""
from contextlib import contextmanager

from alembic import op

from zam_repondeur.models._helpers import alter_pg_enum

# revision identifiers, used by Alembic.
revision = "caaa6d0c7254"
down_revision = "245e371cbf82"
branch_labels = None
depends_on = None


COLUMNS_TO_CONVERT = [
    ("lectures", "chambre"),
    ("textes", "chambre"),
    ("conseils", "chambre"),
]


def upgrade():
    with release_check_constraint():
        alter_pg_enum(
            op, "chambre", ["AN", "SENAT", "CCFP", "CSFPE"], COLUMNS_TO_CONVERT
        )


def downgrade():
    with release_check_constraint():
        alter_pg_enum(op, "chambre", ["AN", "SENAT", "CCFP"], COLUMNS_TO_CONVERT)


@contextmanager
def release_check_constraint():
    op.drop_constraint(op.f("ck_conseils_chambre"), "conseils")
    yield
    op.create_check_constraint(
        op.f("ck_conseils_chambre"), "conseils", "chambre NOT IN ('AN', 'SENAT')",
    )
