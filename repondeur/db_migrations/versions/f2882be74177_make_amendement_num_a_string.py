"""Make amendement num a string

Revision ID: f2882be74177
Revises: 9baaf0db7e30
Create Date: 2020-02-26 17:02:48.798268

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "f2882be74177"
down_revision = "9baaf0db7e30"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("amendements", "num", type_=sa.Text())


def downgrade():
    op.alter_column("amendements", "num", type_=sa.Integer())
