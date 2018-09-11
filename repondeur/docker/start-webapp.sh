#!/bin/bash -e
pipenv run alembic --config=development-docker.ini upgrade head
pipenv run pserve --reload development-docker.ini
