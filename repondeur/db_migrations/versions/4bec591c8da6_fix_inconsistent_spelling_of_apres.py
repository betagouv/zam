"""Fix inconsistent spelling of apres

Revision ID: 4bec591c8da6
Revises: 7373c17f2bf1
Create Date: 2018-10-01 12:54:59.114979

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "4bec591c8da6"
down_revision = "7373c17f2bf1"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("UPDATE articles SET pos='après' WHERE pos='apres';")


def downgrade():
    pass
