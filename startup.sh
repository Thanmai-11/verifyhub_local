#!/bin/bash
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
gunicorn verifyhub.wsgi --bind 0.0.0.0:8000
