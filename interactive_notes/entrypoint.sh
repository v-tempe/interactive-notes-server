#!/bin/sh

echo "Running migrations"
python manage.py migrate --noinput

echo "Starting Gunicorn"
exec gunicorn interactive_notes.wsgi:application --bind 0.0.0.0:8000
