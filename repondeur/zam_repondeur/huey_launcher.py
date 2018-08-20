from zam_repondeur import make_app
from zam_repondeur.tasks.fetch import fetch_amendements, fetch_articles  # noqa

app = make_app(  # type: ignore
    {},
    **{
        "sqlalchemy.url": "sqlite:///repondeur.db",
        "zam.legislature": "15",
        "zam.secret": "dummy",
    }
)
huey = app.huey
