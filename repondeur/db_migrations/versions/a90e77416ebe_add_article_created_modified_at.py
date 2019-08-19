"""Add article created modified at

Revision ID: a90e77416ebe
Revises: bf01601790f4
Create Date: 2019-01-28 13:32:24.093054

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "a90e77416ebe"
down_revision = "bf01601790f4"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "articles",
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
    )
    op.add_column(
        "articles",
        sa.Column(
            "modified_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )


def downgrade():
    op.drop_column("articles", "modified_at")
    op.drop_column("articles", "created_at")
