"""Rename discussion_commune

Revision ID: 73f6d57098fb
Revises: 4a3b250d356d
Create Date: 2018-11-20 09:41:54.876885

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "73f6d57098fb"
down_revision = "4a3b250d356d"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "amendements", "discussion_commune", new_column_name="id_discussion_commune"
    )


def downgrade():
    op.alter_column(
        "amendements", "id_discussion_commune", new_column_name="discussion_commune"
    )
