"""Move ownership to dossier

Revision ID: a4315badfc30
Revises: 5512bb28668f
Create Date: 2019-07-10 15:52:50.997880

"""
from collections import defaultdict

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a4315badfc30"
down_revision = "5512bb28668f"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "dossiers", sa.Column("owned_by_team_pk", sa.Integer(), nullable=True)
    )
    op.create_foreign_key(
        op.f("dossiers_owned_by_team_pk_fkey"),
        "dossiers",
        "teams",
        ["owned_by_team_pk"],
        ["pk"],
    )

    # Transfer ownership from lectures to parent dossiers
    connection = op.get_bind()
    results = connection.execute("SELECT dossier_pk, owned_by_team_pk FROM lectures;")

    ownership = defaultdict(set)
    for dossier_pk, team_pk in results:
        if team_pk is not None:
            ownership[dossier_pk].add(team_pk)

    # Check that all lectures from the same dossier have the same owner
    assert all(len(owners) == 1 for owners in ownership.values()), ownership

    ownership = {dossier_pk: owners.pop() for dossier_pk, owners in ownership.items()}

    for dossier_pk, team_pk in ownership.items():
        connection.execute(
            sa.text(
                """
                UPDATE dossiers
                SET owned_by_team_pk = :team_pk
                WHERE pk = :dossier_pk ;
                """
            ),
            team_pk=team_pk,
            dossier_pk=dossier_pk,
        )

    op.drop_constraint("lectures_owned_by_team_pk_fkey", "lectures", type_="foreignkey")
    op.drop_column("lectures", "owned_by_team_pk")


def downgrade():
    op.add_column(
        "lectures",
        sa.Column("owned_by_team_pk", sa.INTEGER(), autoincrement=False, nullable=True),
    )
    op.create_foreign_key(
        "lectures_owned_by_team_pk_fkey",
        "lectures",
        "teams",
        ["owned_by_team_pk"],
        ["pk"],
    )

    # Transfer ownership from dossiers down to lectures
    connection = op.get_bind()
    results = connection.execute("SELECT pk, owned_by_team_pk FROM dossiers;")
    for dossier_pk, team_pk in results:
        connection.execute(
            sa.text(
                """
                UPDATE lectures
                SET owned_by_team_pk = :team_pk
                WHERE dossier_pk = :dossier_pk ;
                """
            ),
            team_pk=team_pk,
            dossier_pk=dossier_pk,
        )

    op.drop_constraint(
        op.f("dossiers_owned_by_team_pk_fkey"), "dossiers", type_="foreignkey"
    )
    op.drop_column("dossiers", "owned_by_team_pk")
