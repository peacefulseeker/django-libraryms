#! /bin/sh

echo "Applying migrations"
python src/manage.py migrate

if [ "$ENVIRONMENT" = "production" ]; then
    echo "Running in production mode"
    gunicorn -c gunicorn.conf.py
elif [ "$ENVIRONMENT" = "development" ]; then
    echo "Running in development mode"
    python src/manage.py runserver 0.0.0.0:7070
else
    echo "Unknown environment. Exiting."
    exit 1
fi

exec "$@"
