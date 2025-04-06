#!/bin/bash
set -e

function create_db {
    python -c 'import app; app.create_db()'
}

# Ожидание доступности PostgreSQL
echo "Waiting for PostgreSQL..."
while ! pg_isready -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -q -d $POSTGRES_DB; do
  sleep 1
done
echo "PostgreSQL started"

# Ожидание доступности Redis (опционально, но полезно)
echo "Waiting for Redis..."
while ! redis-cli -h $REDIS_HOST -p $REDIS_PORT ping; do
    sleep 1
done
echo "Redis started"


# Применение миграций Alembic
echo "Running Alembic migrations..."
create_db
alembic upgrade head

echo "Starting Uvicorn..."
# Запуск основной команды (переданной в CMD Dockerfile)
exec "$@"