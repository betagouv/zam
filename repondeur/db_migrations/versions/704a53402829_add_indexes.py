"""Add indexes

Revision ID: 704a53402829
Revises: e661a11bf315
Create Date: 2018-10-23 11:41:48.653276

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "704a53402829"
down_revision = "e661a11bf315"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(
        "ix_lectures__chambre__session__num_texte__organe",
        "lectures",
        ["chambre", "session", "num_texte", "organe"],
        unique=True,
    )
    op.create_index("ix_amendements__lecture_pk", "amendements", ["lecture_pk"])
    op.create_index("ix_articles__lecture_pk", "articles", ["lecture_pk"])


def downgrade():
    op.drop_index("ix_articles__lecture_pk")
    op.drop_index("ix_amendements__lecture_pk")
    op.drop_index("ix_lectures__chambre__session__num_texte__organe")
