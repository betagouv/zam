from setuptools import setup

requires = [
    "alembic",
    "bleach",
    "cachecontrol",
    "dataclasses",
    "huey[redis]",
    "inscriptis",
    "lockfile",
    "openpyxl",
    "parsy",
    "pdfkit",
    "psycopg2",
    "pyramid",
    "pyramid-jinja2",
    "pyramid_retry",
    "pyramid_tm",
    "python-redis-lock",
    "redis",
    "requests",
    "rollbar",
    "selectolax",
    "SQLAlchemy>=1.3",
    "SQLAlchemy-Utils",
    "tlfp",
    "transaction",
    "xmltodict",
    "xvfbwrapper",
    "zope.sqlalchemy",
]

setup(
    name="zam-repondeur",
    version="0.1.0",
    url="https://github.com/betagouv/zam",
    install_requires=requires,
    entry_points={
        "paste.app_factory": ["main = zam_repondeur:make_app"],
        "console_scripts": ["zam_worker = zam_repondeur.scripts.worker:main"],
    },
)
