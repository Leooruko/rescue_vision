# Database Setup Instructions

## Issue
The error `no such table: missing_persons` occurs because the database migrations haven't been run yet.

## Solution

### Step 1: Stop the Django Server
If the Django server is running, stop it by pressing `Ctrl+C` in the terminal where it's running.

### Step 2: Delete the Existing Database (if needed)
If you have migration conflicts, delete the database file:
```bash
# Windows
del db.sqlite3

# Linux/Mac
rm db.sqlite3
```

### Step 3: Create Migrations
```bash
python manage.py makemigrations
```

### Step 4: Apply Migrations
```bash
python manage.py migrate
```

### Step 5: Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

### Step 6: Start the Server
```bash
python manage.py runserver
```

## Quick Fix Script

On Windows, you can use the provided `reset_database.bat` script:
1. Stop the Django server
2. Double-click `reset_database.bat`
3. Follow the prompts

## What Gets Created

The migrations will create these tables:
- `users` - User accounts
- `missing_persons` - Missing person cases
- `missing_person_images` - Images for missing persons
- `frames` - Frames from Raspberry Pi
- `notifications` - Detection notifications
- Plus Django's built-in tables (auth, sessions, etc.)

## Troubleshooting

### "Migration admin.0001_initial is applied before its dependency"
This happens when the database was created before custom user model migrations. Solution:
1. Stop the server
2. Delete `db.sqlite3`
3. Run `python manage.py migrate` again

### "Database is locked"
The database file is being used by another process (usually the Django server). Solution:
1. Stop the Django server
2. Wait a few seconds
3. Try again

### "No such module named 'accounts'"
Make sure you're in the project root directory and all apps are properly installed in `settings.py`.
