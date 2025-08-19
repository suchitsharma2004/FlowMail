#!/bin/bash
cd MailProject
export DJANGO_SETTINGS_MODULE=MailProject.settings
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
exec gunicorn MailProject.wsgi:application --bind 0.0.0.0:$PORT
