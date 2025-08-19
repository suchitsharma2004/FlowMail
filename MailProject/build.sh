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

# Check Django setup
python -c "import django; django.setup(); print('Django setup successful')"

# Create any missing migrations
python manage.py makemigrations --noinput

# Run migrations with verbose output
python manage.py migrate --verbosity=2

# Collect static files
python manage.py collectstatic --no-input
