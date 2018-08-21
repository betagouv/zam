from pathlib import Path
from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from zam_repondeur import huey  # noqa
from zam_repondeur.models import DBSession, Base
from zam_repondeur.resources import Root
from zam_repondeur.tasks.fetch import fetch_amendements, fetch_articles  # noqa


HERE = Path(__file__).parent

settings = {
    "sqlalchemy.url": "sqlite:///repondeur.db",
    "zam.legislature": "15",
    "zam.secret": "dummy",
    "zam.an_groups_folder": HERE.parent / "data" / "an" / "groups" / "organe",
}

with Configurator(settings=settings, root_factory=Root) as config:
    config.include("pyramid_tm")
    engine = engine_from_config(settings, "sqlalchemy.")
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
