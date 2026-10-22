# Commands to check which database is being used on production (cPanel)
# Run these in the project directory: /home/corelink/corelink_studio-

# Method 1: Check database configuration
python manage.py diffsettings | grep -A 10 DATABASES

# Method 2: Open Django shell and check
python manage.py shell -c "from django.conf import settings; print('Database Engine:', settings.DATABASES['default']['ENGINE']); print('Database Name:', settings.DATABASES['default']['NAME'])"

# Method 3: Check if PostgreSQL connection works
python manage.py dbshell
# If this opens PostgreSQL shell (psql), then PostgreSQL is being used
# Type \q to exit

# Method 4: Check Django settings directly
python manage.py shell
# Then run:
# from django.conf import settings
# print(settings.DATABASES)
