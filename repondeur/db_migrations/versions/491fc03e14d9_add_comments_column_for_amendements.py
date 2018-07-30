"""Add comments column for amendements

Revision ID: 491fc03e14d9
Revises: cf35ebb8ad69
Create Date: 2018-07-30 10:51:27.246618

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "491fc03e14d9"
down_revision = "cf35ebb8ad69"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("amendements", sa.Column("comments", sa.Text(), nullable=True))


def downgrade():
    op.drop_column("amendements", "comments")
