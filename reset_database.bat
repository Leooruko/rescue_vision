@echo off
echo Stopping Django server if running...
echo Please stop the Django server (Ctrl+C) if it's running, then press any key...
pause

echo Deleting database...
if exist db.sqlite3 del db.sqlite3

echo Running migrations...
python manage.py migrate

echo.
echo Database reset complete!
echo You can now start the server with: python manage.py runserver
pause
