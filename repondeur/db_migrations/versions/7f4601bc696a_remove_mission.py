"""Remove Mission

Revision ID: 7f4601bc696a
Revises: be53f849a248
Create Date: 2019-10-14 14:26:02.512091

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "7f4601bc696a"
down_revision = "be53f849a248"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table("missions")
    op.add_column("amendements", sa.Column("mission_titre", sa.Text(), nullable=True))
    op.add_column(
        "amendements", sa.Column("mission_titre_court", sa.Text(), nullable=True)
    )
    op.drop_constraint("amendements_mission_pk_fkey", "amendements", type_="foreignkey")
    op.drop_column("amendements", "mission_pk")


def downgrade():
    op.add_column(
        "amendements",
        sa.Column("mission_pk", sa.INTEGER(), autoincrement=False, nullable=True),
    )
    op.create_foreign_key(
        "amendements_mission_pk_fkey", "amendements", "missions", ["mission_pk"], ["pk"]
    )
    op.drop_column("amendements", "mission_titre_court")
    op.drop_column("amendements", "mission_titre")
    op.create_table(
        "missions",
        sa.Column("pk", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("titre", sa.TEXT(), autoincrement=False, nullable=True),
        sa.Column("titre_court", sa.TEXT(), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint("pk", name="missions_pkey"),
    )
