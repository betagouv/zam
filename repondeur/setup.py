from setuptools import setup

requires = [
    "alembic",
    "bleach",
    "cachecontrol[filecache]",
    "dataclasses",
    "defusedxml",
    "huey[redis]",
    "inscriptis",
    "lxml",
    "more-itertools",
    "openpyxl",
    "parsy",
    "pdfkit",
    "progressist",
    "psycopg2-binary",
    "pyramid",
    "pyramid-default-cors",
    "pyramid-jinja2",
    "pyramid-mailer",
    "pyramid-retry",
    "pyramid-tm",
    "python-redis-lock",
    "python-slugify",
    "python-throttle",
    "redis",
    "requests",
    "rollbar",
    "selectolax",
    "SQLAlchemy>=1.3",
    "SQLAlchemy-Utils",
    "tlfp",
    "transaction",
    "ujson",
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
        "console_scripts": [
            "zam_worker = zam_repondeur.scripts.worker:main",
            "zam_fetch_amendements = zam_repondeur.scripts.fetch_amendements:main",
            "zam_load_data = zam_repondeur.scripts.load_data:main",
            "zam_reset_data_locks = zam_repondeur.scripts.reset_data_locks:main",
            "zam_whitelist = zam_repondeur.scripts.whitelist:main",
            "zam_admin = zam_repondeur.scripts.admin:main",
            "zam_queue = zam_repondeur.scripts.queue:main",
        ],
    },
)
