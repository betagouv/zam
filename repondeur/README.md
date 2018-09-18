# Répondeur

## Option 1: Docker-based development setup

### Start the environment

Create the Python package metadata (`zam_repondeur.egg_info`) on the host
so that it exists when the app directory is mounted as a volume in the
container (otherwise we would get a DistributionNotFound error at startup):

```
$ python3 setup.py egg_info
```

Build and start the whole system:

```
$ docker-compose up --build --detach
```

You can then access the web app on http://localhost:6543/

You may want to open a shell in the context of one of the containers in order
to run tests or other development-related commands:

```
$ docker-compose exec webapp bash
```

## Option 2: Native local development setup

### Requirements

- Python 3.6+
- Pipenv 2017.1.7
- Postgres
- Redis

### Setup

Install [wkhtmltopdf](https://github.com/JazzCore/python-pdfkit#installation)

```
$ brew install caskroom/cask/wkhtmltopdf
```

```
$ pipenv install
$ pipenv shell
```

Install and run both Redis and Postgres.

### Create the databases

```
$ createuser --createdb zam
$ createdb --owner=zam zam
```

### Initialize the database

```
$ alembic -c development.ini upgrade head
```

### Start the web app

```
$ pserve development.ini --reload
```

You can now access the web app at http://localhost:6543/

### Start the worker for asynchronous tasks

```
$ zam_worker development.ini
```

### Development

Create dedicated table for tests:

```
$ createdb --owner=zam zam-test
```

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
