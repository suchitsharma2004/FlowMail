#!/bin/bash
set -e

echo "🚀 Starting FlowMail with forced migrations..."

# Change to the correct directory
cd MailProject

# Set environment variables
export DJANGO_SETTINGS_MODULE=MailProject.settings
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

echo "📊 Current directory: $(pwd)"
echo "📊 Python path: $PYTHONPATH"

# Test database connection first
echo "🔗 Testing database connection..."
python -c "
import django
django.setup()
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute('SELECT version()')
        result = cursor.fetchone()
        print('✅ Database connected:', result[0][:50])
except Exception as e:
    print('❌ Database connection failed:', str(e))
    exit(1)
"

# Force create migrations
echo "📝 Creating migrations..."
python manage.py makemigrations --noinput

# Force run migrations
echo "🔧 Running migrations..."
python manage.py migrate --noinput --verbosity=2

# Verify tables exist
echo "✅ Verifying tables..."
python -c "
import django
django.setup()
from django.db import connection
from django.contrib.auth.models import User
try:
    count = User.objects.count()
    print(f'✅ Database tables exist. User count: {count}')
except Exception as e:
    print(f'❌ Tables still missing: {e}')
    exit(1)
"

# Start the server
echo "🌟 Starting Gunicorn..."
exec gunicorn MailProject.wsgi:application --bind 0.0.0.0:$PORT
