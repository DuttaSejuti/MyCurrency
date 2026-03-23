#!/bin/sh

if [ "$POSTGRES_HOST" = "db" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $POSTGRES_HOST 5432; do
      sleep 0.1
    done

    echo "Postgres started"
fi

# Run migrations
echo "Running migrations..."
python manage.py migrate

# Start the server
echo "Starting server..."
exec python manage.py runserver 0.0.0.0:8000
