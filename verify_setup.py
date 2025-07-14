#!/usr/bin/env python
"""
Setup verification script for ChatMoji project
Run this after completing the migration fixes
"""

import os
import sys
import django
from django.conf import settings
from django.core.management import execute_from_command_line

def check_requirements():
    """Check if all required components are in place"""
    print("🔍 Checking project setup...")
    
    # Check if manage.py exists
    if not os.path.exists('manage.py'):
        print("❌ manage.py not found. Are you in the right directory?")
        return False
    
    # Check if virtual environment is activated
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Virtual environment not activated. Run: chatmoji_env\\Scripts\\activate")
    
    # Check critical files
    critical_files = [
        'chatmoji_project/settings.py',
        'accounts/models.py',
        'chat/models.py',
        'templates/base.html',
        'requirements.txt'
    ]
    
    for file in critical_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - Missing!")
            return False
    
    return True

def check_database():
    """Check database and migrations"""
    print("\n🗄️  Checking database...")
    
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatmoji_project.settings')
        django.setup()
        
        from django.db import connection
        from django.contrib.auth import get_user_model
        
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            print("✅ Database connection successful")
        
        # Test User model
        User = get_user_model()
        user_count = User.objects.count()
        print(f"✅ User model working - {user_count} users in database")
        
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def check_migrations():
    """Check migration status"""
    print("\n🔄 Checking migrations...")
    
    try:
        from django.core.management import call_command
        from io import StringIO
        
        # Capture output
        out = StringIO()
        call_command('showmigrations', stdout=out)
        output = out.getvalue()
        
        if '[X]' in output:
            print("✅ Migrations applied successfully")
            return True
        else:
            print("❌ Migrations not applied")
            print("Run: python manage.py migrate")
            return False
            
    except Exception as e:
        print(f"❌ Migration check failed: {e}")
        return False

def check_demo_users():
    """Check if demo users exist"""
    print("\n👥 Checking demo users...")
    
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        demo_emails = [
            'john@example.com',
            'jane@example.com',
            'mike@example.com'
        ]
        
        existing_users = User.objects.filter(email__in=demo_emails)
        
        if existing_users.exists():
            print(f"✅ Demo users found: {existing_users.count()}")
            for user in existing_users:
                print(f"   - {user.email} ({user.full_name})")
        else:
            print("⚠️  No demo users found")
            print("Run: python manage.py create_demo_users")
        
        return True
    except Exception as e:
        print(f"❌ Demo user check failed: {e}")
        return False

def run_test_server():
    """Test if server can start"""
    print("\n🚀 Testing server startup...")
    
    try:
        from django.core.management import call_command
        from django.test.utils import override_settings
        
        # Try to run check command
        call_command('check')
        print("✅ Django check passed")
        
        print("✅ Server should start successfully")
        print("Run: python manage.py runserver")
        
        return True
    except Exception as e:
        print(f"❌ Server test failed: {e}")
        return False

def main():
    """Main verification function"""
    print("🎉 ChatMoji Setup Verification")
    print("=" * 50)
    
    all_checks = [
        check_requirements(),
        check_database(),
        check_migrations(),
        check_demo_users(),
        run_test_server()
    ]
    
    print("\n" + "=" * 50)
    if all(all_checks):
        print("🎉 ALL CHECKS PASSED!")
        print("Your ChatMoji project is ready!")
        print("\nNext steps:")
        print("1. Run: python manage.py runserver")
        print("2. Visit: http://127.0.0.1:8000")
        print("3. Login with demo users or create new account")
        print("\nDemo login: john@example.com / password123")
    else:
        print("❌ Some checks failed.")
        print("Please fix the issues above and run this script again.")
    
    print("=" * 50)

if __name__ == "__main__":
    main()