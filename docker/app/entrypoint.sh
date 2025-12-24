#!/bin/sh
set -e

# Run migrations if it's a Django app
python manage.py migrate --noinput

exec "$@"
