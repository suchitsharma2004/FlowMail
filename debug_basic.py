#!/usr/bin/env python3
"""
Simple Django debug script to test basic functionality
"""
import os
import sys
from pathlib import Path

# Add the MailProject directory to Python path
BASE_DIR = Path(__file__).resolve().parent / 'MailProject'
sys.path.insert(0, str(BASE_DIR))

# Set environment variables
os.environ.setdefault('DATABASE_URL', 'postgresql://neondb_owner:npg_TsrilzJ4OR3B@ep-orange-sky-a12mgfbb-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MailProject.settings')

print("🔧 Testing basic Django setup...")

try:
    # Test Django import
    print("1. Testing Django import...")
    import django
    print(f"   ✅ Django version: {django.get_version()}")
    
    # Test settings import
    print("2. Testing settings import...")
    django.setup()
    from django.conf import settings
    print(f"   ✅ Settings loaded, DEBUG: {settings.DEBUG}")
    
    # Test database configuration
    print("3. Testing database configuration...")
    db_config = settings.DATABASES['default']
    print(f"   ✅ Database ENGINE: {db_config['ENGINE']}")
    print(f"   ✅ Database NAME: {db_config['NAME'][:50]}...")
    
    # Test basic model imports
    print("4. Testing model imports...")
    from django.contrib.auth.models import User
    from mailapp.models import UserProfile, Project, Mail
    print("   ✅ All models imported successfully")
    
    # Test forms import
    print("5. Testing forms import...")
    from mailapp.forms import CustomUserCreationForm
    print("   ✅ Forms imported successfully")
    
    print("\n🎉 All basic tests passed! Django setup is working.")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
