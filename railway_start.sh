#!/bin/bash
set -e  # Exit on any error

echo "=== Starting Railway deployment ==="
echo "PORT: ${PORT:-Not set}"
echo "DATABASE_URL: ${DATABASE_URL:0:30}..."
echo "RAILWAY_ENVIRONMENT: ${RAILWAY_ENVIRONMENT:-Not set}"
echo "Python version: $(python --version)"
echo "Current directory: $(pwd)"
echo "Directory contents:"
ls -la

# Set environment variables
export DJANGO_SETTINGS_MODULE=ehr_system.settings
export PYTHONUNBUFFERED=1

# Run migrations
echo ""
echo "=== Running migrations ==="
python manage.py migrate --noinput || echo "Migration failed but continuing..."

# Collect static files
echo ""
echo "=== Collecting static files ==="
python manage.py collectstatic --noinput --clear || echo "Static collection failed but continuing..."

# Test WSGI application
echo ""
echo "=== Testing WSGI application ==="
python -c "from ehr_system.wsgi import application; print('WSGI test successful')" || {
    echo "WSGI test failed!"
    echo "Python path:"
    python -c "import sys; print('\n'.join(sys.path))"
    exit 1
}

# Start Gunicorn
echo ""
echo "=== Starting Gunicorn ==="
echo "Command: gunicorn ehr_system.wsgi:application --bind 0.0.0.0:${PORT:-8000}"

exec gunicorn ehr_system.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 2 \
    --threads 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level debug \
    --capture-output \
    --enable-stdio-inheritance \
    --preload