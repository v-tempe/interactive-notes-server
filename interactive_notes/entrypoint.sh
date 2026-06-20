#!/bin/sh

echo "Collecting static"
python manage.py collectstatic --noinput

echo "Running migrations"
python manage.py migrate --noinput

echo "Creating superuser"
python init_admin.py

echo "Starting Gunicorn"
exec gunicorn interactive_notes.wsgi:application --bind 0.0.0.0:8000
