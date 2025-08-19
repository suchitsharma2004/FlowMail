#!/usr/bin/env bash
# exit on error
set -o errexit

# Change to the MailProject directory
cd "$(dirname "$0")"

# Install dependencies
pip install -r ../requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate
