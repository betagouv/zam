"""Dossier order

Revision ID: 1f6afe6eb1a9
Revises: 08e2b571d519
Create Date: 2020-03-20 16:56:13.203061

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "1f6afe6eb1a9"
down_revision = "08e2b571d519"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("dossiers", sa.Column("order", sa.Integer(), nullable=True))


def downgrade():
    op.drop_column("dossiers", "order")
