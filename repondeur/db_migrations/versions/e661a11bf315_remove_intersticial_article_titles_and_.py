"""Remove intersticial article titles and contents

Revision ID: e661a11bf315
Revises: e8a500ef478d
Create Date: 2018-10-12 09:56:50.579936

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "e661a11bf315"
down_revision = "e8a500ef478d"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("UPDATE articles SET titre='', contenu=NULL WHERE pos!='';")


def downgrade():
    pass
