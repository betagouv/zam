"""Add affectation to amendements

Revision ID: 6756d255959a
Revises: 068feac86821
Create Date: 2018-11-07 11:20:34.396535

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "6756d255959a"
down_revision = "068feac86821"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("amendements", sa.Column("affectation", sa.Text(), nullable=True))


def downgrade():
    op.drop_column("amendements", "affectation")
