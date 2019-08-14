"""Add unique constraint on amendement position

Revision ID: cbb2e504c783
Revises: cfdd95041347
Create Date: 2018-12-07 21:14:08.246565

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "cbb2e504c783"
down_revision = "cfdd95041347"
branch_labels = None
depends_on = None


def upgrade():
    op.create_unique_constraint(None, "amendements", ["position", "lecture_pk"])


def downgrade():
    op.drop_constraint(None, "amendements", type_="unique")
