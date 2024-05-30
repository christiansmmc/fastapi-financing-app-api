echo "Running migrations..."
alembic upgrade head

echo "Starting application..."
fastapi dev app/main.py