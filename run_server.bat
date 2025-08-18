@echo off
echo Starting EHR Evaluation System...
echo.

echo [1/4] Running database migrations...
python manage.py makemigrations
python manage.py migrate

echo.
echo [2/4] Creating superuser (if not exists)...
echo from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin123') | python manage.py shell

echo.
echo [3/4] Collecting static files...
python manage.py collectstatic --noinput

echo.
echo [4/4] Starting Django server...
echo Server will be available at: http://localhost:8000
echo Admin panel: http://localhost:8000/admin
echo API: http://localhost:8000/api
echo.
python manage.py runserver