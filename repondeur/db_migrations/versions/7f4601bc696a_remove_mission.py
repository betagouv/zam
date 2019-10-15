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
    op.add_column("amendements", sa.Column("mission_titre", sa.Text(), nullable=True))
    op.add_column(
        "amendements", sa.Column("mission_titre_court", sa.Text(), nullable=True)
    )
    op.execute(
        """
        UPDATE amendements
        SET mission_titre=missions.titre, mission_titre_court=missions.titre_court
        FROM missions
        WHERE missions.pk = amendements.mission_pk;
    """
    )
    op.drop_constraint("amendements_mission_pk_fkey", "amendements", type_="foreignkey")
    op.drop_column("amendements", "mission_pk")
    op.drop_table("missions")


def downgrade():
    raise NotImplementedError
