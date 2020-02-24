"""Add AN sort key

Revision ID: 9baaf0db7e30
Revises: 16b0715d5eee
Create Date: 2020-02-12 21:00:43.265552

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "9baaf0db7e30"
down_revision = "16b0715d5eee"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("amendements", sa.Column("tri_amendement", sa.Text(), nullable=True))
    op.create_index(
        "ix_amendements__tri_amendement",
        "amendements",
        ["tri_amendement"],
        unique=False,
    )


def downgrade():
    op.drop_index("ix_amendements__tri_amendement", table_name="amendements")
    op.drop_column("amendements", "tri_amendement")
