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

# Show database info for debugging
echo "=== Database Configuration ==="
python -c "
import os
print('DATABASE_URL:', os.getenv('DATABASE_URL', 'NOT SET'))
print('DJANGO_SETTINGS_MODULE:', os.getenv('DJANGO_SETTINGS_MODULE', 'NOT SET'))
"

# Check Django setup
echo "=== Testing Django Setup ==="
python -c "
import django
import os
django.setup()
print('Django setup successful')

from django.conf import settings
print('Database ENGINE:', settings.DATABASES['default']['ENGINE'])
print('Database NAME:', settings.DATABASES['default']['NAME'][:50] + '...' if len(settings.DATABASES['default']['NAME']) > 50 else settings.DATABASES['default']['NAME'])
"

# Test database connection
echo "=== Testing Database Connection ==="
python -c "
import django
django.setup()
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute('SELECT version()')
        result = cursor.fetchone()
        print('Database connection successful:', result[0][:50] + '...')
except Exception as e:
    print('Database connection failed:', str(e))
"

# Create any missing migrations
echo "=== Creating Migrations ==="
python manage.py makemigrations --noinput

# Show migration status
echo "=== Migration Status ==="
python manage.py showmigrations

# Run migrations with verbose output
echo "=== Running Migrations ==="
python manage.py migrate --verbosity=2

# Verify tables exist
echo "=== Verifying Tables ==="
python -c "
import django
django.setup()
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute('SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = %s', ['public'])
    count = cursor.fetchone()[0]
    print(f'Tables created: {count}')
"

# Collect static files
echo "=== Collecting Static Files ==="
python manage.py collectstatic --no-input

echo "=== Build Complete ==="
