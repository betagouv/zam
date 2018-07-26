"""Add jaune column for articles

Revision ID: 3d120d80713d
Revises: b86ab6e391df
Create Date: 2018-07-26 14:37:38.974347

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3d120d80713d"
down_revision = "b86ab6e391df"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "amendements", sa.Column("subdiv_jaune", sa.PickleType(), nullable=True)
    )


def downgrade():
    op.drop_column("amendements", "subdiv_jaune")
