#!/usr/bin/env python3
"""
Manual migration script for MailProject
Run this if automatic migrations fail during deployment
"""
import os
import sys
import django
from pathlib import Path

# Add the MailProject directory to Python path
BASE_DIR = Path(__file__).resolve().parent / 'MailProject'
sys.path.insert(0, str(BASE_DIR))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MailProject.settings')

try:
    print("🔧 Setting up Django...")
    django.setup()
    print("✅ Django setup successful")
    
    print("\n🔧 Testing database connection...")
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT version()")
        result = cursor.fetchone()
        print(f"✅ Database connected: {result[0][:50]}...")
    
    print("\n🔧 Running migrations...")
    from django.core.management import execute_from_command_line
    
    # Run makemigrations
    print("Creating migrations...")
    execute_from_command_line(['manage.py', 'makemigrations'])
    
    # Run migrate
    print("Applying migrations...")
    execute_from_command_line(['manage.py', 'migrate', '--verbosity=2'])
    
    print("\n🔧 Verifying tables...")
    with connection.cursor() as cursor:
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        tables = cursor.fetchall()
        print(f"✅ Tables created: {len(tables)}")
        for table in tables[:10]:  # Show first 10 tables
            print(f"  - {table[0]}")
        if len(tables) > 10:
            print(f"  ... and {len(tables) - 10} more")
    
    print("\n🎉 Migration completed successfully!")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
