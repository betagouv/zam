"""Add conseils lectures relationship

Revision ID: fe0f5eb2cc56
Revises: caaa6d0c7254
Create Date: 2020-03-13 11:27:03.486594

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "fe0f5eb2cc56"
down_revision = "caaa6d0c7254"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "conseils_lectures",
        sa.Column("conseil_id", sa.Integer(), nullable=True),
        sa.Column("lecture_pk", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["conseil_id"],
            ["conseils.id"],
            name=op.f("conseils_lectures_conseil_id_fkey"),
        ),
        sa.ForeignKeyConstraint(
            ["lecture_pk"],
            ["lectures.pk"],
            name=op.f("conseils_lectures_lecture_pk_fkey"),
        ),
    )


def downgrade():
    op.drop_table("conseils_lectures")
