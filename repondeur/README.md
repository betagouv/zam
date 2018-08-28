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

## Start the web app

```
$ pserve development.ini --reload
```

You can now access the web app at http://localhost:6543/

## Start the worker for asynchronous tasks

```
$ zam_worker development.ini
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
