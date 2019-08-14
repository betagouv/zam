"""Add creation and modification dates to amendements

Revision ID: 1fdb28a1773a
Revises: 704a53402829
Create Date: 2018-10-25 16:28:47.032935

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "1fdb28a1773a"
down_revision = "704a53402829"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "amendements",
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
    )
    op.add_column(
        "amendements",
        sa.Column(
            "modified_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
    )


def downgrade():
    op.drop_column("amendements", "modified_at")
    op.drop_column("amendements", "created_at")
