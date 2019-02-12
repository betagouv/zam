"""Set unique email constraint for users

Revision ID: c92b4d05aba8
Revises: a760e877b6ce
Create Date: 2019-01-30 13:16:41.948844

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "c92b4d05aba8"
down_revision = "a760e877b6ce"
branch_labels = None
depends_on = None


def upgrade():
    op.create_unique_constraint(None, "users", ["email"])


def downgrade():
    op.drop_constraint(None, "users", type_="unique")
