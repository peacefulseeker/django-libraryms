#!/usr/bin/env bash
# Exit on error
set -o errexit

pip install --upgrade pip
pip install poetry==1.8.3

poetry install

# Convert static asset files
poetry run python src/manage.py collectstatic --no-input

# Apply any outstanding database migrations
poetry run python src/manage.py migrate

poetry run python src/manage.py shell <<EOF
from apps.users.models import User
try:
    User.objects.create_superuser('${ADMIN_USERNAME}', '${ADMIN_EMAIL}', '${ADMIN_PASSWORD}')
    print('Admin created')
except Exception as e:
    print(str(e))
EOF
