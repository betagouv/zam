"""Add CSFPE chambre

Revision ID: caaa6d0c7254
Revises: 95dfdcde1955
Create Date: 2020-03-11 17:19:11.567332

"""
from alembic import op

from zam_repondeur.models._helpers import alter_pg_enum

# revision identifiers, used by Alembic.
revision = "caaa6d0c7254"
down_revision = "95dfdcde1955"
branch_labels = None
depends_on = None


COLUMNS_TO_CONVERT = [
    ("lectures", "chambre"),
    ("textes", "chambre"),
    ("conseils", "chambre"),
]


def upgrade():
    alter_pg_enum(op, "chambre", ["AN", "SENAT", "CCFP", "CSFPE"], COLUMNS_TO_CONVERT)


def downgrade():
    alter_pg_enum(op, "chambre", ["AN", "SENAT", "CCFP"], COLUMNS_TO_CONVERT)
