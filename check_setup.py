#!/usr/bin/env python
"""
Diagnostic script to check for common setup issues.
Run this before starting the Django server to identify problems.
"""
import sys

def check_python_version():
    """Check Python version."""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("⚠️  WARNING: Python 3.8+ is required")
        return False
    print("✓ Python version OK")
    return True

def check_opencv():
    """Check if OpenCV is available."""
    try:
        import cv2
        version = cv2.__version__
        print(f"✓ OpenCV version: {version}")
        
        # Check if Haar Cascade can be loaded
        try:
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            cascade = cv2.CascadeClassifier(cascade_path)
            if cascade.empty():
                print("⚠️  WARNING: Haar Cascade classifier file not found")
                print(f"   Tried: {cascade_path}")
                return False
            print(f"✓ Haar Cascade loaded from: {cascade_path}")
            return True
        except Exception as e:
            print(f"⚠️  WARNING: Failed to load Haar Cascade: {str(e)}")
            return False
    except ImportError:
        print("❌ ERROR: OpenCV (cv2) is not installed")
        print("   Install via: sudo apt-get install python3-opencv")
        print("   Or: pip install opencv-python")
        return False

def check_django():
    """Check if Django is available."""
    try:
        import django
        print(f"✓ Django version: {django.__version__}")
        return True
    except ImportError:
        print("❌ ERROR: Django is not installed")
        print("   Install via: pip install -r requirements.txt")
        return False

def check_dependencies():
    """Check other required dependencies."""
    dependencies = {
        'numpy': 'numpy',
        'PIL': 'Pillow',
        'rest_framework': 'djangorestframework',
    }
    
    all_ok = True
    for module, package in dependencies.items():
        try:
            __import__(module)
            print(f"✓ {package} installed")
        except ImportError:
            print(f"❌ ERROR: {package} is not installed")
            print(f"   Install via: pip install {package}")
            all_ok = False
    
    return all_ok

def check_face_recognition_removed():
    """Check that face-recognition and dlib are NOT installed."""
    removed_packages = {
        'face_recognition': 'face-recognition',
        'dlib': 'dlib',
    }
    
    all_ok = True
    for module, package in removed_packages.items():
        try:
            __import__(module)
            print(f"⚠️  WARNING: {package} is still installed (should be removed)")
            print(f"   Uninstall via: pip uninstall {package}")
            all_ok = False
        except ImportError:
            print(f"✓ {package} not installed (correct)")
    
    return all_ok

def main():
    """Run all checks."""
    print("=" * 60)
    print("Rescue Vision - Setup Diagnostic")
    print("=" * 60)
    print()
    
    checks = [
        ("Python Version", check_python_version),
        ("OpenCV", check_opencv),
        ("Django", check_django),
        ("Dependencies", check_dependencies),
        ("Removed Packages", check_face_recognition_removed),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n[{name}]")
        result = check_func()
        results.append((name, result))
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    all_passed = all(result for _, result in results)
    
    for name, result in results:
        status = "✓ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    if all_passed:
        print("\n✓ All checks passed! You can run: python manage.py runserver")
        return 0
    else:
        print("\n❌ Some checks failed. Please fix the issues above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
