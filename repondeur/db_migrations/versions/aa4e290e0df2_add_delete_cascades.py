"""Add delete cascades

Revision ID: aa4e290e0df2
Revises: d535af9f8a61
Create Date: 2019-08-28 15:37:37.101589

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "aa4e290e0df2"
down_revision = "d535af9f8a61"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint(
        "amendement_user_contents_amendement_pk_fkey",
        "amendement_user_contents",
        type_="foreignkey",
    )
    op.create_foreign_key(
        op.f("amendement_user_contents_amendement_pk_fkey"),
        "amendement_user_contents",
        "amendements",
        ["amendement_pk"],
        ["pk"],
        ondelete="cascade",
    )

    op.drop_constraint("amendements_lecture_pk_fkey", "amendements", type_="foreignkey")
    op.create_foreign_key(
        op.f("amendements_lecture_pk_fkey"),
        "amendements",
        "lectures",
        ["lecture_pk"],
        ["pk"],
        ondelete="cascade",
    )

    op.drop_constraint(
        "article_user_contents_article_pk_fkey",
        "article_user_contents",
        type_="foreignkey",
    )
    op.create_foreign_key(
        op.f("article_user_contents_article_pk_fkey"),
        "article_user_contents",
        "articles",
        ["article_pk"],
        ["pk"],
        ondelete="cascade",
    )

    op.drop_constraint("articles_lecture_pk_fkey", "articles", type_="foreignkey")
    op.create_foreign_key(
        op.f("articles_lecture_pk_fkey"),
        "articles",
        "lectures",
        ["lecture_pk"],
        ["pk"],
        ondelete="cascade",
    )

    op.drop_constraint("events_amendement_pk_fkey", "events", type_="foreignkey")
    op.create_foreign_key(
        op.f("events_amendement_pk_fkey"),
        "events",
        "amendements",
        ["amendement_pk"],
        ["pk"],
        ondelete="cascade",
    )

    op.drop_constraint("events_article_pk_fkey", "events", type_="foreignkey")
    op.create_foreign_key(
        op.f("events_article_pk_fkey"),
        "events",
        "articles",
        ["article_pk"],
        ["pk"],
        ondelete="cascade",
    )

    op.drop_constraint("events_lecture_pk_fkey", "events", type_="foreignkey")
    op.create_foreign_key(
        op.f("events_lecture_pk_fkey"),
        "events",
        "lectures",
        ["lecture_pk"],
        ["pk"],
        ondelete="cascade",
    )

    op.drop_constraint(
        "shared_tables_lecture_pk_fkey", "shared_tables", type_="foreignkey"
    )
    op.create_foreign_key(
        op.f("shared_tables_lecture_pk_fkey"),
        "shared_tables",
        "lectures",
        ["lecture_pk"],
        ["pk"],
        ondelete="cascade",
    )

    op.drop_constraint("user_tables_lecture_pk_fkey", "user_tables", type_="foreignkey")
    op.create_foreign_key(
        op.f("user_tables_lecture_pk_fkey"),
        "user_tables",
        "lectures",
        ["lecture_pk"],
        ["pk"],
        ondelete="cascade",
    )


def downgrade():
    op.drop_constraint(
        op.f("user_tables_lecture_pk_fkey"), "user_tables", type_="foreignkey"
    )
    op.create_foreign_key(
        "user_tables_lecture_pk_fkey", "user_tables", "lectures", ["lecture_pk"], ["pk"]
    )

    op.drop_constraint(
        op.f("shared_tables_lecture_pk_fkey"), "shared_tables", type_="foreignkey"
    )
    op.create_foreign_key(
        "shared_tables_lecture_pk_fkey",
        "shared_tables",
        "lectures",
        ["lecture_pk"],
        ["pk"],
    )

    op.drop_constraint(op.f("events_lecture_pk_fkey"), "events", type_="foreignkey")
    op.create_foreign_key(
        "events_lecture_pk_fkey", "events", "lectures", ["lecture_pk"], ["pk"]
    )

    op.drop_constraint(op.f("events_article_pk_fkey"), "events", type_="foreignkey")
    op.create_foreign_key(
        "events_article_pk_fkey", "events", "articles", ["article_pk"], ["pk"]
    )

    op.drop_constraint(op.f("events_amendement_pk_fkey"), "events", type_="foreignkey")
    op.create_foreign_key(
        "events_amendement_pk_fkey", "events", "amendements", ["amendement_pk"], ["pk"]
    )

    op.drop_constraint(op.f("articles_lecture_pk_fkey"), "articles", type_="foreignkey")
    op.create_foreign_key(
        "articles_lecture_pk_fkey", "articles", "lectures", ["lecture_pk"], ["pk"]
    )

    op.drop_constraint(
        op.f("article_user_contents_article_pk_fkey"),
        "article_user_contents",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "article_user_contents_article_pk_fkey",
        "article_user_contents",
        "articles",
        ["article_pk"],
        ["pk"],
    )

    op.drop_constraint(
        op.f("amendements_lecture_pk_fkey"), "amendements", type_="foreignkey"
    )
    op.create_foreign_key(
        "amendements_lecture_pk_fkey", "amendements", "lectures", ["lecture_pk"], ["pk"]
    )

    op.drop_constraint(
        op.f("amendement_user_contents_amendement_pk_fkey"),
        "amendement_user_contents",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "amendement_user_contents_amendement_pk_fkey",
        "amendement_user_contents",
        "amendements",
        ["amendement_pk"],
        ["pk"],
    )
