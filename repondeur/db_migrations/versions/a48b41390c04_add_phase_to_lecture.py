"""Add phase to Lecture

Revision ID: a48b41390c04
Revises: 2a464485a750
Create Date: 2019-09-19 09:35:23.410202

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "a48b41390c04"
down_revision = "2a464485a750"
branch_labels = None
depends_on = None


phase_type = sa.Enum(
    "INCONNUE",
    "PREMIERE_LECTURE",
    "DEUXIEME_LECTURE",
    "NOUVELLE_LECTURE",
    "LECTURE_DEFINITIVE",
    name="phase",
)


def upgrade():
    phase_type.create(op.get_bind())

    op.add_column("lectures", sa.Column("phase", phase_type, nullable=True))
    op.execute(
        """
        UPDATE lectures
        SET phase = 'PREMIERE_LECTURE'
        WHERE phase IS NULL AND titre LIKE 'Première lecture %';
    """
    )
    op.execute(
        """
        UPDATE lectures
        SET phase = 'DEUXIEME_LECTURE'
        WHERE phase IS NULL AND titre LIKE 'Deuxième lecture %';
    """
    )
    op.execute(
        """
        UPDATE lectures
        SET phase = 'NOUVELLE_LECTURE'
        WHERE phase IS NULL AND titre LIKE 'Nouvelle lecture %';
    """
    )
    op.execute(
        """
        UPDATE lectures
        SET phase = 'LECTURE_DEFINITIVE'
        WHERE phase IS NULL AND titre LIKE 'Lecture définitive %';
    """
    )
    op.alter_column("lectures", "phase", nullable=False)


def downgrade():
    op.drop_column("lectures", "phase")
    phase_type.drop(op.get_bind())
