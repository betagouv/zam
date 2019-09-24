"""User admins

Revision ID: be53f849a248
Revises: a48b41390c04
Create Date: 2019-09-24 12:13:35.088399

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "be53f849a248"
down_revision = "a48b41390c04"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("admin_at", sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column("users", "admin_at")
