"""Add CCFP chambre

Revision ID: 3fe97532ba21
Revises: f2882be74177
Create Date: 2020-02-27 14:25:49.524626

"""
from alembic import op

from zam_repondeur.models._helpers import alter_pg_enum

# revision identifiers, used by Alembic.
revision = "3fe97532ba21"
down_revision = "f2882be74177"
branch_labels = None
depends_on = None


COLUMNS_TO_CONVERT = [("lectures", "chambre"), ("textes", "chambre")]


def upgrade():
    alter_pg_enum(op, "chambre", ["AN", "SENAT", "CCFP"], COLUMNS_TO_CONVERT)


def downgrade():
    alter_pg_enum(op, "chambre", ["AN", "SENAT"], COLUMNS_TO_CONVERT)
