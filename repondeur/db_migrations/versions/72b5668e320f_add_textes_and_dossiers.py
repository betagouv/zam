"""Add textes and dossiers

Revision ID: 72b5668e320f
Revises: e4d4f35b9df7
Create Date: 2019-04-04 14:13:37.173464

"""
from datetime import datetime

import sqlalchemy as sa
from alembic import op

from zam_repondeur.services.fetch.an.dossiers.dossiers_legislatifs import (
    get_dossiers_legislatifs_and_textes,
)

LEGISLATURES = [14, 15]


# revision identifiers, used by Alembic.
revision = "72b5668e320f"
down_revision = "e4d4f35b9df7"
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()

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
        sa.Column("chambre", sa.Enum("AN", "SENAT", name="chambre"), nullable=False),
        sa.Column("session", sa.Integer(), nullable=True),
        sa.Column("legislature", sa.Integer(), nullable=True),
        sa.Column("numero", sa.Integer(), nullable=False),
        sa.Column("titre_long", sa.Text(), nullable=False),
        sa.Column("titre_court", sa.Text(), nullable=False),
        sa.Column("date_depot", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("modified_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("pk"),
        sa.UniqueConstraint("uid", name=op.f("textes_uid_key")),
    )
    op.create_index(
        "uq_textes_chambre_session_legislature_numero_key",
        "textes",
        ["chambre", "session", "legislature", "numero"],
        unique=True,
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
    dossiers_by_uid, _ = get_dossiers_legislatifs_and_textes(*LEGISLATURES)

    now = datetime.utcnow()

    print("Creating dossiers...")
    op.bulk_insert(
        dossiers_table,
        [
            {"uid": uid, "titre": dossier.titre, "created_at": now, "modified_at": now}
            for uid, dossier in dossiers_by_uid.items()
        ],
    )

    print("Creating textes...")
    textes = {
        lecture.texte
        for dossier in dossiers_by_uid.values()
        for lecture in dossier.lectures
    }
    textes_data = [
        {
            "uid": texte.uid,
            "type_": texte.type_.name,
            "chambre": texte.chambre.name,
            "session": texte.session,
            "legislature": texte.legislature,
            "numero": texte.numero,
            "titre_long": texte.titre_long,
            "titre_court": texte.titre_court,
            "date_depot": texte.date_depot,
            "created_at": now,
            "modified_at": now,
        }
        for texte in textes
    ]
    op.bulk_insert(textes_table, textes_data)

    print("Linking lectures to the right dossiers and textes...")
    lectures = connection.execute(
        "SELECT pk, chambre, session, num_texte, dossier_legislatif FROM lectures;"
    )
    for lecture in lectures:
        texte = _find_texte_from_lecture(connection, lecture)
        dossier = _find_dossier_by_titre(
            connection, dossiers_table, lecture.dossier_legislatif
        )
        connection.execute(
            f"UPDATE lectures SET texte_pk = {texte.pk}, dossier_pk = {dossier.pk} "
            f"WHERE pk = {lecture.pk};"
        )

    op.drop_column("lectures", "num_texte")
    op.drop_column("lectures", "dossier_legislatif")


def _find_texte_from_lecture(connection, lecture):
    if lecture.chambre == "an":
        chambre = "AN"
        session_or_legislature_key = "legislature"
        session_or_legislature_value = int(lecture.session)
    elif lecture.chambre == "senat":
        chambre = "SENAT"
        session_or_legislature_key = "session"
        session_or_legislature_value = int(lecture.session.split("-")[0])
    else:
        raise NotImplementedError
    textes = connection.execute(
        f"SELECT pk FROM textes "
        f"WHERE chambre = '{chambre}' "
        f"  AND {session_or_legislature_key} = {session_or_legislature_value} "
        f"  AND numero = {lecture.num_texte} "
        f"LIMIT 1;"
    )
    try:
        return next(textes)
    except StopIteration:
        raise ValueError("Could not find texte")


def _find_dossier_by_titre(connection, dossiers_table, titre):
    # The dossier's title may have changed since the lecture was created.
    # We do a prefix search to cover a case we saw where text was added at the end.
    query = dossiers_table.select().where(dossiers_table.c.titre.like(titre + "%"))
    matches = connection.execute(query).fetchall()
    if len(matches) == 0:
        raise ValueError(f"Could not find dossier for {titre} (no matches)")
    if len(matches) > 1:
        for match in matches:
            print(match)
        raise ValueError(f"Could not find dossier for {titre} (multiple matches)")
    return matches[0]


def downgrade():
    raise NotImplementedError
