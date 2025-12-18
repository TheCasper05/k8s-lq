#!/bin/bash

set -e

# # Wait for database to be ready
# echo "Waiting for database..."
# while ! nc -z db 5432; do
#   sleep 10
# done
# echo "Database is ready!"

# # Wait for Redis to be ready
# echo "Waiting for Redis..."
# while ! nc -z redis 6379; do
#   sleep 10
# done
# echo "Redis is ready!"

# Function to run Django management commands
run_django_command() {
    uv run python manage.py "$@"
}

# Execute based on the command argument
case "$1" in
    server)
        echo "Running migrations..."
        run_django_command migrate --noinput

        echo "Collecting static files..."
        run_django_command collectstatic --noinput

        echo "Starting Gunicorn server..."
        uv run gunicorn config.wsgi:application \
            --bind 0.0.0.0:8000 \
            --workers 4 \
            --threads 2 \
            --timeout 60 \
            --access-logfile - \
            --error-logfile - \
            --log-level info
        ;;

    server-dev)
        echo "Running migrations..."
        run_django_command migrate --noinput

        echo "Collecting static files..."
        run_django_command collectstatic --noinput

        echo "Starting Django development server..."
        uv run python manage.py runserver 0.0.0.0:8000
        ;;

    celery-worker)
        echo "Starting Celery worker..."
        uv run celery -A config worker --loglevel=info --concurrency=4
        ;;

    # celery-beat)
    #     echo "Starting Celery beat scheduler..."
    #     uv run celery -A config beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
    #     ;;

    celery-flower)
        echo "Starting Celery Flower monitoring..."
        uv run celery -A config flower --port=5555 --address=0.0.0.0
        ;;

    migrate)
        echo "Running migrations..."
        run_django_command migrate --noinput
        ;;

    makemigrations)
        echo "Creating migrations..."
        run_django_command makemigrations
        ;;

    createsuperuser)
        echo "Creating superuser..."
        run_django_command createsuperuser
        ;;

    shell)
        echo "Starting Django shell..."
        run_django_command shell
        ;;

    test)
        echo "Running tests..."
        uv run pytest
        ;;

    bash)
        echo "Starting bash shell..."
        /bin/bash
        ;;

    *)
        echo "Available commands:"
        echo "  server          - Start Gunicorn production server"
        echo "  server-dev      - Start Django development server"
        echo "  celery-worker   - Start Celery worker"
        # echo "  celery-beat     - Start Celery beat scheduler"
        echo "  celery-flower   - Start Celery Flower monitoring"
        echo "  migrate         - Run database migrations"
        echo "  makemigrations  - Create new migrations"
        echo "  createsuperuser - Create Django superuser"
        echo "  shell           - Start Django shell"
        echo "  test            - Run tests"
        echo "  bash            - Start bash shell"
        exit 1
        ;;
esac
#  docker build . -t registry.digitalocean.com/lq-registry/dj-backend:qa-latest
#  docker push registry.digitalocean.com/lq-registry/dj-backend:qa-latest
#  doctl apps create-deployment de02d338-6db0-4c53-b0da-3077a62fd3ea