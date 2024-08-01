#! /bin/sh

# Exit on error
set -o errexit

python src/manage.py migrate
python src/manage.py runserver 0.0.0.0:7070

exec "$@"
