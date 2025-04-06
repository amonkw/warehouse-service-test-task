# Этап 1: Сборка зависимостей
FROM python:3.11-slim as builder

WORKDIR /build

# Копирование файла зависимостей и установка
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Этап 2: Основной образ
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends postgresql-client redis-tools && \
    rm -rf /var/lib/apt/lists/*

# Копирование установленных зависимостей из builder'а
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Копирование кода приложения
COPY ./app /app/app
COPY alembic.ini /app/alembic.ini
# Копирование скрипта точки входа
COPY ./docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

# Указываем порт, который слушает FastAPI (uvicorn)
EXPOSE 8000

# Точка входа
ENTRYPOINT ["/app/docker-entrypoint.sh"]

# Команда по умолчанию (будет выполнена после entrypoint)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
