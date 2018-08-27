from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from zam_repondeur import huey  # noqa
from zam_repondeur.models import DBSession, Base
from zam_repondeur.resources import Root
from zam_repondeur.tasks.fetch import *  # noqa
from zam_repondeur.tasks.periodic import *  # noqa


settings = {
    "sqlalchemy.url": "sqlite:///repondeur.db",
    "zam.legislature": "15",
    "zam.secret": "dummy",
}

with Configurator(settings=settings, root_factory=Root) as config:
    config.include("pyramid_tm")
    engine = engine_from_config(settings, "sqlalchemy.")
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
