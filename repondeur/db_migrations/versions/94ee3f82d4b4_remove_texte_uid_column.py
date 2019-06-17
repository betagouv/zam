"""Remove texte uid column

Revision ID: 94ee3f82d4b4
Revises: e8813e77a748
Create Date: 2019-06-17 14:14:36.052374

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "94ee3f82d4b4"
down_revision = "e8813e77a748"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint("textes_uid_key", "textes", type_="unique")
    op.drop_column("textes", "uid")


def downgrade():
    raise NotImplementedError("Would need to retrieve uids from TexteRefs.")
