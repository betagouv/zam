#!/bin/bash -e
alembic --config=development-docker.ini upgrade head
pserve --reload development-docker.ini
