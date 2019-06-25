#!/bin/bash
set -o errexit
alembic --config=development-docker.ini upgrade head
zam_load_data development-docker.ini
pserve --reload development-docker.ini
