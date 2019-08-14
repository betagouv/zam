"""Add activation for dossiers

Revision ID: c1b9e0409596
Revises: 3801b54623bc
Create Date: 2019-07-11 16:57:58.530118

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "c1b9e0409596"
down_revision = "3801b54623bc"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("dossiers", sa.Column("activated_at", sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column("dossiers", "activated_at")
