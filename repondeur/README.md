# Répondeur

## Requirements

Python 3.6+
Redis

## Setup

Install [wkhtmltopdf](https://github.com/JazzCore/python-pdfkit#installation)

```
$ brew install caskroom/cask/wkhtmltopdf
```

```
$ pipenv install
$ pipenv shell
```

Install and run Redis.

## Initialize the database

```
$ alembic -c development.ini upgrade head
```

## Extra setup

Get the groups data for Assemblée nationale:

```
$ curl --silent --show-error http://data.assemblee-nationale.fr/static/openData/repository/15/amo/deputes_actifs_mandats_actifs_organes_divises/AMO40_deputes_actifs_mandats_actifs_organes_divises_XV.json.zip -o groups.zip
$ mkdir -p data/an/groups
$ unzip -q -o groups.zip -d data/an/groups/
$ rm groups.zip
```

## Start the web app

```
$ pserve development.ini --reload
```

You can now access the web app at http://localhost:6543/

## Start asynchronous tasks

```
$ huey_consumer zam_repondeur.huey_launcher.huey
```

## Development

Run tests:

```
$ pytest
```

Reformat code:

```
$ black .
```

Check style guide:

```
$ flake8
```

Check type annotations:

```
mypy zam_repondeur
```
