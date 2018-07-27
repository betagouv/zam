"""Add jaune column for articles

Revision ID: cf35ebb8ad69
Revises: d42ed17375d6
Create Date: 2018-07-27 09:56:07.533858

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "cf35ebb8ad69"
down_revision = "d42ed17375d6"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("amendements", sa.Column("subdiv_jaune", sa.Text(), nullable=True))


def downgrade():
    op.drop_column("amendements", "subdiv_jaune")
