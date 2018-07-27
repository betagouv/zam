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
    with op.batch_alter_table("amendements") as batch_op:
        batch_op.add_column(
            sa.Column(
                "parent_num",
                sa.Integer(),
                sa.ForeignKey("amendements.num", name="fk_amendements_parent_num"),
                nullable=True,
            )
        )
        batch_op.add_column(sa.Column("parent_rectif", sa.Integer(), nullable=True))


def downgrade():
    with op.batch_alter_table("amendements") as batch_op:
        batch_op.drop_column("parent_rectif")
        batch_op.drop_column("parent_num")
