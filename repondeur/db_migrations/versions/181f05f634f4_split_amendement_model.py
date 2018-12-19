"""Split Amendement model

Revision ID: 181f05f634f4
Revises: e749824546cc
Create Date: 2018-12-10 13:57:09.336882

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "181f05f634f4"
down_revision = "e749824546cc"
branch_labels = None
depends_on = None


def upgrade():
    amendement_user_contents = op.create_table(
        "amendement_user_contents",
        sa.Column("pk", sa.Integer(), nullable=False),
        sa.Column("avis", sa.Text(), nullable=True),
        sa.Column("objet", sa.Text(), nullable=True),
        sa.Column("reponse", sa.Text(), nullable=True),
        sa.Column("affectation", sa.Text(), nullable=True),
        sa.Column("comments", sa.Text(), nullable=True),
        sa.Column("bookmarked_at", sa.DateTime(), nullable=True),
        sa.Column("amendement_pk", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["amendement_pk"], ["amendements.pk"]),
        sa.PrimaryKeyConstraint("pk"),
    )
    connection = op.get_bind()
    results = connection.execute(
        """
        SELECT pk, avis, observations, reponse, affectation, comments, bookmarked_at
        FROM amendements
        """
    )
    op.bulk_insert(
        amendement_user_contents,
        [
            {
                "amendement_pk": pk,
                "avis": avis,
                "objet": obs,
                "reponse": reponse,
                "affectation": affectation,
                "comments": comments,
                "bookmarked_at": bookmarked_at,
            }
            for pk, avis, obs, reponse, affectation, comments, bookmarked_at in results
        ],
    )
    op.drop_column("amendements", "observations")
    op.drop_column("amendements", "comments")
    op.drop_column("amendements", "reponse")
    op.drop_column("amendements", "affectation")
    op.drop_column("amendements", "avis")


def downgrade():
    pass
