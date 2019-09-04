#!/bin/bash
set -o errexit
alembic --config=development-docker.ini upgrade head
zam_load_data development-docker.ini
zam_whitelist development-docker.ini add *@*.gouv.fr || true
pserve --reload development-docker.ini app=zam_webapp
