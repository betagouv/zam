"""Store amendement identique ID

Revision ID: cfdd95041347
Revises: 73f6d57098fb
Create Date: 2018-11-20 10:28:26.499863

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "cfdd95041347"
down_revision = "73f6d57098fb"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("amendements", sa.Column("id_identique", sa.Integer(), nullable=True))
    op.execute("UPDATE amendements SET id_identique = id_discussion_commune;")
    op.drop_column("amendements", "identique")


def downgrade():
    op.add_column("amendements", sa.Column("identique", sa.Boolean(), nullable=True))
    op.execute(
        """
        UPDATE amendements
        SET identique = (
            CASE WHEN id_identique IS NULL
            THEN
                NULL
            ELSE
                true
            END
        );
    """
    )
    op.drop_column("amendements", "id_identique")
