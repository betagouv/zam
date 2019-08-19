"""Remove bookmarked_at column

Revision ID: d80c1fac4582
Revises: 06e826937905
Create Date: 2019-01-21 12:51:22.744731

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "d80c1fac4582"
down_revision = "06e826937905"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("amendement_user_contents", "bookmarked_at")

    # This one should have been dropped in 181f05f634f4
    op.drop_column("amendements", "bookmarked_at")


def downgrade():
    op.add_column(
        "amendements",
        sa.Column(
            "bookmarked_at", postgresql.TIMESTAMP(), autoincrement=False, nullable=True
        ),
    )
    op.add_column(
        "amendement_user_contents",
        sa.Column(
            "bookmarked_at", postgresql.TIMESTAMP(), autoincrement=False, nullable=True
        ),
    )
