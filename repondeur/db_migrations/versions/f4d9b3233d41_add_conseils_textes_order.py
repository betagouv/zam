"""Add conseils textes order

Revision ID: f4d9b3233d41
Revises: 08e2b571d519
Create Date: 2020-03-23 14:59:26.902024

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "f4d9b3233d41"
down_revision = "08e2b571d519"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "conseils_lectures", sa.Column("position", sa.Integer(), nullable=True)
    )
    op.create_primary_key(
        "pk_conseils_lecture", "conseils_lectures", ["conseil_id", "lecture_pk"]
    )
    op.drop_constraint(
        "conseils_lectures_conseil_id_fkey", "conseils_lectures", type_="foreignkey"
    )
    op.drop_constraint(
        "conseils_lectures_lecture_pk_fkey", "conseils_lectures", type_="foreignkey"
    )
    op.create_foreign_key(
        op.f("conseils_lectures_lecture_pk_fkey"),
        "conseils_lectures",
        "lectures",
        ["lecture_pk"],
        ["pk"],
        onupdate="CASCADE",
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        op.f("conseils_lectures_conseil_id_fkey"),
        "conseils_lectures",
        "conseils",
        ["conseil_id"],
        ["id"],
        onupdate="CASCADE",
        ondelete="CASCADE",
    )


def downgrade():
    op.drop_constraint(
        op.f("conseils_lectures_conseil_id_fkey"),
        "conseils_lectures",
        type_="foreignkey",
    )
    op.drop_constraint(
        op.f("conseils_lectures_lecture_pk_fkey"),
        "conseils_lectures",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "conseils_lectures_lecture_pk_fkey",
        "conseils_lectures",
        "lectures",
        ["lecture_pk"],
        ["pk"],
    )
    op.create_foreign_key(
        "conseils_lectures_conseil_id_fkey",
        "conseils_lectures",
        "conseils",
        ["conseil_id"],
        ["id"],
    )
    op.drop_constraint("pk_conseils_lecture", "conseils_lectures")
    op.drop_column("conseils_lectures", "position")
