"""New models

Revision ID: a3962c18da56
Revises:
Create Date: 2018-08-17 10:38:50.315368

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "a3962c18da56"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "lectures",
        sa.Column("pk", sa.Integer(), nullable=False),
        sa.Column("chambre", sa.Text(), nullable=True),
        sa.Column("session", sa.Text(), nullable=True),
        sa.Column("num_texte", sa.Integer(), nullable=True),
        sa.Column("organe", sa.Text(), nullable=True),
        sa.Column("titre", sa.Text(), nullable=True),
        sa.Column("dossier_legislatif", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("modified_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("pk"),
    )
    op.create_table(
        "articles",
        sa.Column("pk", sa.Integer(), nullable=False),
        sa.Column("lecture_pk", sa.Integer(), nullable=False),
        sa.Column("type", sa.Text(), nullable=True),
        sa.Column("num", sa.Text(), nullable=True),
        sa.Column("mult", sa.Text(), nullable=True),
        sa.Column("pos", sa.Text(), nullable=True),
        sa.Column("titre", sa.Text(), nullable=True),
        sa.Column("contenu", sa.PickleType(), nullable=True),
        sa.Column("jaune", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("pk"),
        sa.ForeignKeyConstraint(["lecture_pk"], ["lectures.pk"]),
    )
    op.create_table(
        "amendements",
        sa.Column("pk", sa.Integer(), nullable=False),
        sa.Column("num", sa.Integer(), nullable=False),
        sa.Column("rectif", sa.Integer(), nullable=False),
        sa.Column("auteur", sa.Text(), nullable=True),
        sa.Column("matricule", sa.Text(), nullable=True),
        sa.Column("groupe", sa.Text(), nullable=True),
        sa.Column("date_depot", sa.Date(), nullable=True),
        sa.Column("sort", sa.Text(), nullable=True),
        sa.Column("position", sa.Integer(), nullable=True),
        sa.Column("discussion_commune", sa.Integer(), nullable=True),
        sa.Column("identique", sa.Boolean(), nullable=True),
        sa.Column("dispositif", sa.Text(), nullable=True),
        sa.Column("objet", sa.Text(), nullable=True),
        sa.Column("resume", sa.Text(), nullable=True),
        sa.Column("alinea", sa.Text(), nullable=True),
        sa.Column("parent_pk", sa.Integer(), nullable=True),
        sa.Column("parent_rectif", sa.Integer(), nullable=True),
        sa.Column("lecture_pk", sa.Integer(), nullable=True),
        sa.Column("article_pk", sa.Integer(), nullable=True),
        sa.Column("avis", sa.Text(), nullable=True),
        sa.Column("observations", sa.Text(), nullable=True),
        sa.Column("reponse", sa.Text(), nullable=True),
        sa.Column("comments", sa.Text(), nullable=True),
        sa.Column("bookmarked_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["article_pk"], ["articles.pk"]),
        sa.ForeignKeyConstraint(["lecture_pk"], ["lectures.pk"]),
        sa.ForeignKeyConstraint(["parent_pk"], ["amendements.pk"]),
        sa.PrimaryKeyConstraint("pk"),
        sa.UniqueConstraint("num", "lecture_pk"),
    )


def downgrade():
    op.drop_table("amendements")
    op.drop_table("articles")
    op.drop_table("lectures")
