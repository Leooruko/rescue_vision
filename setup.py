#!/usr/bin/env python
"""
Setup script for Rescue Vision Django project.
Run this after installing dependencies to set up the database and create a superuser.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rescue_vision.settings')
django.setup()

from django.core.management import call_command
from django.contrib.auth import get_user_model

def main():
    print("Rescue Vision - Setup Script")
    print("=" * 50)
    
    # Run migrations
    print("\n1. Running migrations...")
    call_command('makemigrations')
    call_command('migrate')
    print("✓ Migrations completed")
    
    # Create superuser (optional)
    print("\n2. Create superuser? (y/n): ", end='')
    create_superuser = input().strip().lower()
    
    if create_superuser == 'y':
        call_command('createsuperuser')
        print("✓ Superuser created")
    else:
        print("  Skipped superuser creation")
    
    # Create media directories
    print("\n3. Creating media directories...")
    os.makedirs('media/missing_person_images', exist_ok=True)
    os.makedirs('media/frames', exist_ok=True)
    os.makedirs('media/detection_images', exist_ok=True)
    os.makedirs('media/embeddings', exist_ok=True)
    print("✓ Media directories created")
    
    print("\n" + "=" * 50)
    print("Setup completed successfully!")
    print("\nTo start the development server, run:")
    print("  python manage.py runserver")
    print("\nThen visit: http://127.0.0.1:8000/")

if __name__ == '__main__':
    main()
