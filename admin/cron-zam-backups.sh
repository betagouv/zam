#!/bin/sh

BACKUP_DIR=/var/backups/zam

sudo -Hiu postgres LANG="C.UTF-8" LC_CTYPE="C.UTF-8" \
    pg_dump --dbname=zam --create --encoding=UTF8 \
    --file=$BACKUP_DIR/postgres-dump-$(date --utc --iso-8601=seconds).sql

# See: https://pypi.org/project/rotate-backups/ for options
rotate-backups --prefer-recent --relaxed --include='*.sql' \
    --hourly=24 \
    --daily=30 \
    --weekly=4 \
    --monthly=12 \
    --yearly=always \
    $BACKUP_DIR
