"""Add initial tables

Revision ID: b86ab6e391df
Revises:
Create Date: 2018-07-25 16:22:14.347590

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b86ab6e391df"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "lectures",
        sa.Column("chambre", sa.Text(), nullable=False),
        sa.Column("session", sa.Text(), nullable=False),
        sa.Column("num_texte", sa.Integer(), nullable=False),
        sa.Column("organe", sa.Text(), nullable=False),
        sa.Column("titre", sa.Text(), nullable=True),
        sa.Column("dossier_legislatif", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("modified_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("chambre", "session", "num_texte", "organe"),
    )
    op.create_table(
        "amendements",
        sa.Column("chambre", sa.Text(), nullable=False),
        sa.Column("session", sa.Text(), nullable=False),
        sa.Column("num_texte", sa.Integer(), nullable=False),
        sa.Column("organe", sa.Integer(), nullable=False),
        sa.Column("subdiv_type", sa.Text(), nullable=False),
        sa.Column("subdiv_num", sa.Text(), nullable=False),
        sa.Column("subdiv_mult", sa.Text(), nullable=True),
        sa.Column("subdiv_pos", sa.Text(), nullable=True),
        sa.Column("alinea", sa.Text(), nullable=True),
        sa.Column("subdiv_titre", sa.Text(), nullable=True),
        sa.Column("subdiv_contenu", sa.PickleType(), nullable=True),
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
        sa.Column("avis", sa.Text(), nullable=True),
        sa.Column("observations", sa.Text(), nullable=True),
        sa.Column("reponse", sa.Text(), nullable=True),
        sa.Column("bookmarked_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["chambre", "session", "num_texte", "organe"],
            [
                "lectures.chambre",
                "lectures.session",
                "lectures.num_texte",
                "lectures.organe",
            ],
        ),
        sa.PrimaryKeyConstraint("chambre", "session", "num_texte", "organe", "num"),
    )


def downgrade():
    op.drop_table("amendements")
    op.drop_table("lectures")
