"""Added amendement parent column

Revision ID: 753db774ddb8
Revises: b86ab6e391df
Create Date: 2018-07-25 14:35:34.920375

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "753db774ddb8"
down_revision = "b86ab6e391df"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("amendements", sa.Column("parent", sa.Text(), nullable=True))


def downgrade():
    op.drop_column("amendements", "parent")
