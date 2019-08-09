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

### Install requirements

#### Python 3.6+

To install Python 3 (macOS):

```
$ brew install python
```

#### PostgreSQL

To install PostgreSQL (macOS):

```
$ brew install postgresql
```

#### Redis

To install Redis (macOS):

```
$ brew install redis
```

#### wkhtmltopdf

To install [wkhtmltopdf](https://github.com/JazzCore/python-pdfkit#installation) (macOS):

```
$ brew install caskroom/cask/wkhtmltopdf
```

### Setup the Python virtual environment

Create a Python virtual environment and install dependencies:

```
$ python3 -m venv ~/.virtualenvs/zam
$ source ~/.virtualenvs/zam/bin/activate
(zam)$ pip install -r requirements.txt
(zam)$ pip install -r requirements-dev.txt
(zam)$ pip install -e .
```

### Create the database

```
$ createuser --createdb zam
$ createdb --owner=zam zam
```

### Initialize the database

```
(zam)$ alembic -c development.ini upgrade head
```

### Load data from external sources

Fetch (open)data from AN and Sénat websites to be able to create
up-to-date lectures.

```
(zam)$ zam_load_data development.ini
```

### Start the web app

```
(zam)$ pserve --reload development.ini app=zam_webapp
```

You can now access the web app at http://localhost:6543/

### Start the worker for asynchronous tasks

```
(zam)$ zam_worker development.ini#worker
```

### Development

Create a separate database for tests:

```
$ createdb --owner=zam zam-test
```

Run tests:

```
(zam)$ pytest
```

Reformat code:

```
(zam)$ black .
```

Check style guide:

```
(zam)$ flake8
```

Check type annotations:

```
(zam)$ mypy zam_repondeur
```
