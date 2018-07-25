"""Add amendement parent columns

Revision ID: d42ed17375d6
Revises: b86ab6e391df
Create Date: 2018-07-25 16:55:38.474157

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d42ed17375d6"
down_revision = "b86ab6e391df"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("amendements", sa.Column("parent_num", sa.Integer(), nullable=True))
    op.add_column(
        "amendements", sa.Column("parent_rectif", sa.Integer(), nullable=True)
    )


def downgrade():
    op.drop_column("amendements", "parent_rectif")
    op.drop_column("amendements", "parent_num")
