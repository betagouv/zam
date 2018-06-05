from setuptools import setup

requires = ["pyramid", "pyramid-jinja2"]

setup(
    name="zam-repondeur",
    version="0.1.0",
    url="https://github.com/betagouv/zam",
    install_requires=requires,
    entry_points="""\
      [paste.app_factory]
      main = zam_repondeur:make_app
      """,
)
