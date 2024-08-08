#! /bin/bash

python -m gunicorn --bind :8000 --chdir src --workers 2 core.wsgi:application
