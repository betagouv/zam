"""Add textes and dossiers

Revision ID: f41d1f52bd17
Revises: e4d4f35b9df7
Create Date: 2019-04-03 17:02:30.251982

"""
from datetime import datetime

from alembic import op
import sqlalchemy as sa

from zam_repondeur.fetch.an.dossiers.dossiers_legislatifs import (
    get_dossiers_legislatifs
)


LEGISLATURES = [14, 15]


# revision identifiers, used by Alembic.
revision = "f41d1f52bd17"
down_revision = "e4d4f35b9df7"
branch_labels = None
depends_on = None


def upgrade():
    dossiers_table = op.create_table(
        "dossiers",
        sa.Column("pk", sa.Integer(), nullable=False),
        sa.Column("uid", sa.Text(), nullable=False),
        sa.Column("titre", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("modified_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("pk"),
    )
    textes_table = op.create_table(
        "textes",
        sa.Column("pk", sa.Integer(), nullable=False),
        sa.Column("uid", sa.Text(), nullable=False),
        sa.Column(
            "type_", sa.Enum("PROJET", "PROPOSITION", name="typetexte"), nullable=False
        ),
        sa.Column("numero", sa.Integer(), nullable=False),
        sa.Column("titre_long", sa.Text(), nullable=False),
        sa.Column("titre_court", sa.Text(), nullable=False),
        sa.Column("date_depot", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("modified_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("pk"),
    )
    op.add_column("lectures", sa.Column("dossier_pk", sa.Integer(), nullable=True))
    op.add_column("lectures", sa.Column("texte_pk", sa.Integer(), nullable=True))
    op.create_index(
        "ix_lectures__chambre__session__partie__organe",
        "lectures",
        ["chambre", "session", "partie", "organe"],
        unique=True,
    )
    op.drop_index(
        "ix_lectures__chambre__session__num_texte__partie__organe",
        table_name="lectures",
    )
    op.create_foreign_key(
        op.f("lectures_dossier_pk_fkey"), "lectures", "dossiers", ["dossier_pk"], ["pk"]
    )
    op.create_foreign_key(
        op.f("lectures_texte_pk_fkey"), "lectures", "textes", ["texte_pk"], ["pk"]
    )

    # Get the data
    dossiers_by_uid = get_dossiers_legislatifs(*LEGISLATURES)

    now = datetime.utcnow()

    # Create the dossiers
    op.bulk_insert(
        dossiers_table,
        [
            {"uid": uid, "titre": dossier.titre, "created_at": now, "modified_at": now}
            for uid, dossier in dossiers_by_uid.items()
        ],
    )

    # Create the textes
    textes = {
        lecture.texte
        for dossier in dossiers_by_uid.values()
        for lecture in dossier.lectures
    }
    op.bulk_insert(
        textes_table,
        [
            {
                "uid": texte.uid,
                "type_": texte.type_.name,
                "numero": texte.numero,
                "titre_long": texte.titre_long,
                "titre_court": texte.titre_court,
                "date_depot": texte.date_depot,
                "created_at": now,
                "modified_at": now,
            }
            for texte in textes
        ],
    )

    # Update lectures with foreign keys
    connection = op.get_bind()
    lectures = connection.execute(
        "SELECT pk, session, num_texte, dossier_legislatif FROM lectures;"
    )
    for lecture in lectures:
        texte = next(
            connection.execute(
                f"SELECT pk FROM textes WHERE numero = {lecture.num_texte} LIMIT 1;"
            )
        )
        dossier = next(
            connection.execute(
                f"SELECT pk FROM dossiers "
                f"WHERE titre = '{lecture.dossier_legislatif}' LIMIT 1;"
            )
        )
        connection.execute(
            f"UPDATE lectures SET texte_pk = {texte.pk}, dossier_pk = {dossier.pk} "
            f"WHERE pk = {lecture.pk};"
        )

    op.drop_column("lectures", "num_texte")
    op.drop_column("lectures", "dossier_legislatif")

    assert False


def downgrade():
    op.add_column(
        "lectures",
        sa.Column("dossier_legislatif", sa.TEXT(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "lectures",
        sa.Column("num_texte", sa.INTEGER(), autoincrement=False, nullable=True),
    )
    op.drop_constraint(op.f("lectures_texte_pk_fkey"), "lectures", type_="foreignkey")
    op.drop_constraint(op.f("lectures_dossier_pk_fkey"), "lectures", type_="foreignkey")

    # TODO: Convert foreign keys into column values.

    op.create_index(
        "ix_lectures__chambre__session__num_texte__partie__organe",
        "lectures",
        ["chambre", "session", "num_texte", "partie", "organe"],
        unique=True,
    )
    op.drop_index(
        "ix_lectures__chambre__session__partie__organe", table_name="lectures"
    )
    op.drop_column("lectures", "texte_pk")
    op.drop_column("lectures", "dossier_pk")
    op.drop_table("textes")
    op.drop_table("dossiers")
