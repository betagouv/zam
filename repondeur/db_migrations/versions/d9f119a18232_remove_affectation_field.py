"""Remove affectation field

Revision ID: d9f119a18232
Revises: 13c75654057a
Create Date: 2019-01-31 14:45:07.427658

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d9f119a18232"
down_revision = "13c75654057a"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("amendement_user_contents", "affectation")


def downgrade():
    op.add_column(
        "amendement_user_contents",
        sa.Column("affectation", sa.TEXT(), autoincrement=False, nullable=True),
    )
