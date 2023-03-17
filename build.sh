#!/usr/bin/env bash
# exit on error
set -o errexit

poetry install

cd bible_bffs

python manage.py collectstatic --no-input
python manage.py migrate