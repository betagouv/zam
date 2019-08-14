"""Add partie column to lectures

Revision ID: 15301bb743b1
Revises: 1fdb28a1773a
Create Date: 2018-10-29 13:00:00.763459

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "15301bb743b1"
down_revision = "1fdb28a1773a"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("lectures", sa.Column("partie", sa.Integer(), nullable=True))
    op.execute(
        "UPDATE lectures SET partie = 1 WHERE dossier_legislatif LIKE '%finances%';"
    )
    op.drop_index("ix_lectures__chambre__session__num_texte__organe")
    op.create_index(
        "ix_lectures__chambre__session__num_texte__partie__organe",
        "lectures",
        ["chambre", "session", "num_texte", "partie", "organe"],
        unique=True,
    )


def downgrade():
    op.drop_index("ix_lectures__chambre__session__num_texte__partie__organe")
    op.drop_column("lectures", "partie")
    op.create_index(
        "ix_lectures__chambre__session__num_texte__organe",
        "lectures",
        ["chambre", "session", "num_texte", "organe"],
        unique=True,
    )
