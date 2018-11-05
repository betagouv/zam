"""Move observations to reponse for government amendements

Revision ID: 068feac86821
Revises: 15301bb743b1
Create Date: 2018-11-05 14:29:44.080790

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "068feac86821"
down_revision = "15301bb743b1"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        UPDATE amendements
        SET reponse = observations, observations = ''
        WHERE auteur = 'LE GOUVERNEMENT';
    """
    )


def downgrade():
    op.execute(
        """
        UPDATE amendements
        SET observations = reponse, reponse = ''
        WHERE auteur = 'LE GOUVERNEMENT';
    """
    )
