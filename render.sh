#!/usr/bin/env bash
set -o errexit

python manage.py migrate
python manage.py collectstatic --noinput
gunicorn gerenciamento_hoteleiro.wsgi:application --bind 0.0.0.0:10000