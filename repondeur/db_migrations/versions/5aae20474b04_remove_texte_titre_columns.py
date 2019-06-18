"""Remove Texte titre columns

Revision ID: 5aae20474b04
Revises: 94ee3f82d4b4
Create Date: 2019-06-18 13:46:04.499762

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5aae20474b04"
down_revision = "94ee3f82d4b4"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("textes", "titre_court")
    op.drop_column("textes", "titre_long")


def downgrade():
    op.add_column(
        "textes",
        sa.Column("titre_long", sa.TEXT(), autoincrement=False, nullable=False),
    )
    op.add_column(
        "textes",
        sa.Column("titre_court", sa.TEXT(), autoincrement=False, nullable=False),
    )
