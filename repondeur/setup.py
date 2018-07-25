from setuptools import setup

requires = [
    "bleach",
    "cachecontrol",
    "dataclasses",
    "inscriptis",
    "lockfile",
    "openpyxl",
    "pdfkit",
    "pyramid",
    "pyramid-jinja2",
    "pyramid_retry",
    "pyramid_tm",
    "requests",
    "selectolax",
    "SQLAlchemy",
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
    entry_points={"paste.app_factory": ["main = zam_repondeur:make_app"]},
)
