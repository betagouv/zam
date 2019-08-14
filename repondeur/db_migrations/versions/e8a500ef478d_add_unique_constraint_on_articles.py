"""Add unique constraint on articles

Revision ID: e8a500ef478d
Revises: 4bec591c8da6
Create Date: 2018-10-03 12:47:26.769497

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "e8a500ef478d"
down_revision = "4bec591c8da6"
branch_labels = None
depends_on = None


def upgrade():
    op.create_unique_constraint(
        "articles_lecture_pk_type_num_mult_pos_key",
        "articles",
        ["lecture_pk", "type", "num", "mult", "pos"],
    )


def downgrade():
    op.drop_constraint(
        "articles_lecture_pk_type_num_mult_pos_key", "articles", type_="unique"
    )
