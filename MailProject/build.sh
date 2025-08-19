#!/usr/bin/env bash
# exit on error
set -o errexit

# Change to the MailProject directory
cd "$(dirname "$0")"

# Install dependencies
pip install --upgrade pip
pip install -r ../requirements.txt

# Set Django settings module
export DJANGO_SETTINGS_MODULE=MailProject.settings

# Add current directory to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate
