#!/usr/bin/env python3
"""
Debug script to test database connection and common issues on Render
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
    django.setup()
    print("✅ Django setup successful")
    
    # Test database connection
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        if result:
            print("✅ Database connection successful")
        
    # Test if tables exist
    from django.core.management import execute_from_command_line
    print("📋 Checking migrations...")
    
    # Check if User model works
    from django.contrib.auth.models import User
    user_count = User.objects.count()
    print(f"✅ User table accessible, count: {user_count}")
    
    # Check if our app models work
    from mailapp.models import UserProfile, Project
    profile_count = UserProfile.objects.count()
    project_count = Project.objects.count()
    print(f"✅ MailApp models accessible - Profiles: {profile_count}, Projects: {project_count}")
    
    print("\n🎉 All database checks passed!")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    print(f"Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
