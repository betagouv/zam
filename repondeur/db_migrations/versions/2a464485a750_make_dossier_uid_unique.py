"""Make Dossier UID unique

Revision ID: 2a464485a750
Revises: d42c23832d27
Create Date: 2019-09-06 14:43:20.100223

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "2a464485a750"
down_revision = "d42c23832d27"
branch_labels = None
depends_on = None


def upgrade():
    op.create_unique_constraint(op.f("dossiers_uid_key"), "dossiers", ["uid"])


def downgrade():
    op.drop_constraint(op.f("dossiers_uid_key"), "dossiers", type_="unique")
