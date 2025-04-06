# Сервис мониторинга состояния складов

Микросервис на Python/FastAPI для обработки сообщений из Kafka о перемещениях товаров между складами, учета остатков и предоставления API для доступа к данным.

[![Python Version](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-FastAPI-green.svg)](https://fastapi.tiangolo.com/)
[![Database](https://img.shields.io/badge/Database-PostgreSQL-blue.svg)](https://www.postgresql.org/)
[![Broker](https://img.shields.io/badge/Broker-Kafka-black.svg)](https://kafka.apache.org/)
[![Cache](https://img.shields.io/badge/Cache-Redis-red.svg)](https://redis.io/)
[![Testing](https://img.shields.io/badge/Testing-Pytest-informational.svg)](https://pytest.org/)
[![Dockerized](https://img.shields.io/badge/Dockerized-Yes-blue.svg)](https://www.docker.com/)

## Описание

Этот сервис решает задачу отслеживания движения товаров между складами. Он слушает топик Kafka (или принимает сообщения через вебхук), обрабатывает события прибытия (`arrival`) и отбытия (`departure`), обновляет текущие остатки товаров на складах в базе данных PostgreSQL и предоставляет REST API для получения информации о конкретных перемещениях и актуальных остатках.

## Основные возможности

*   ✅ **Обработка Kafka сообщений:** Прием и обработка сообщений о перемещениях товаров (прибытие/отбытие) через фоновый консьюмер `aiokafka` или через эндпоинт-вебхук.
*   ✅ **Хранение данных:** Сохранение истории перемещений (отправитель, получатель, товар, количество, время) и актуальных остатков в PostgreSQL с использованием SQLAlchemy.
*   ✅ **Контроль остатков:** Обеспечение неотрицательности количества товаров на складе при операциях списания.
*   ✅ **REST API:** Предоставление эндпоинтов FastAPI для:
    *   Получения информации о конкретном перемещении (`/api/v1/movements/{movement_id}`).
    *   Получения текущего остатка товара на складе (`/api/v1/warehouse/{warehouse_id}/products/{product_id}`).
*   ✅ **OpenAPI документация:** Автоматически генерируемая и доступная документация API (Swagger UI и ReDoc).
*   ✅ **Кэширование:** Использование Redis для кэширования ответов API для повышения производительности (опциональная задача).
*   ✅ **Тестирование:** Покрытие кода юнит-тестами с использованием Pytest (опциональная задача).
*   ✅ **Docker:** Полная конфигурация для запуска сервиса и всех его зависимостей (PostgreSQL, Redis, Kafka) с помощью Docker Compose.

## Технологический стек

*   **Язык:** Python 3.11+
*   **Фреймворк:** FastAPI
*   **Брокер сообщений:** Apache Kafka (используется `aiokafka`)
*   **База данных:** PostgreSQL
*   **ORM:** SQLAlchemy 2.x (async)
*   **Миграции:** Alembic
*   **Кэш:** Redis (используется `redis[hiredis]`)
*   **Валидация данных:** Pydantic V2
*   **Тестирование:** Pytest, pytest-asyncio, HTTPX
*   **Контейнеризация:** Docker, Docker Compose
*   ** ASGI сервер:** Uvicorn

## Начало работы (с использованием Docker)

### Предварительные требования

*   Docker ([Install Docker Engine](https://docs.docker.com/engine/install/))
*   Docker Compose ([Install Docker Compose](https://docs.docker.com/compose/install/))

### Установка и запуск

1.  **Клонируйте репозиторий:**
    ```bash
    git clone <your-repository-url>
    cd <repository-directory>
    ```

2.  **Создайте файл `.env`:**
    Скопируйте `.env.example` в `.env` и при необходимости измените значения (особенно пароли и порты, если они конфликтуют с вашими локальными).
    *Важно:* Установите `APP_MODE=kafka` в `.env`, если хотите, чтобы сервис запускал фоновый Kafka консьюмер. Оставьте `APP_MODE=webhook_only` (по умолчанию), если планируете отправлять сообщения только через API вебхук.

3.  **Соберите Docker образы:**
    ```bash
    docker compose build
    ```

4.  **Запустите сервисы:**
    ```bash
    docker compose up -d
    ```
    При первом запуске Docker Compose скачает образы PostgreSQL, Redis, Kafka (если включен), создаст контейнеры и сети. Скрипт `docker-entrypoint.sh` внутри контейнера `app` дождется доступности БД и Redis, применит миграции Alembic и запустит Uvicorn сервер.

### Доступ к сервису

*   **API:** Сервис будет доступен по адресу `http://localhost:<APP_PORT>` (по умолчанию `http://localhost:8000`).
*   **OpenAPI (Swagger UI):** `http://localhost:<APP_PORT>/docs`
*   **OpenAPI (ReDoc):** `http://localhost:<APP_PORT>/redoc`

### Просмотр логов

```bash
docker compose logs -f app      # Логи FastAPI приложения
docker compose logs -f db       # Логи PostgreSQL
docker compose logs -f redis    # Логи Redis
docker compose logs -f kafka    # Логи Kafka (если запущен)
```

### Остановка сервисов

```bash
docker compose down          # Остановить и удалить контейнеры
# docker compose down -v     # Остановить, удалить контейнеры и тома (данные будут потеряны!)
```

## Работа с Kafka

Сервис может работать в двух режимах (задается переменной `APP_MODE` в `.env`):

1.  **`kafka`:** Запускается фоновый процесс (`kafka_consumer.py`), который подключается к Kafka (указанному в `KAFKA_BOOTSTRAP_SERVERS` и `KAFKA_TOPIC`) и обрабатывает сообщения.
2.  **`webhook_only` (по умолчанию):** Фоновый консьюмер не запускается. Сообщения можно отправлять вручную через API эндпоинт для тестирования или имитации поступления из Kafka.

### Эндпоинт для имитации Kafka сообщений

*   **URL:** `/api/v1/kafka/webhook`
*   **Метод:** `POST`
*   **Тело запроса:** JSON, соответствующий схеме `KafkaWebhookRequest` (см. примеры ниже или `/docs`).

**Пример отправки сообщения через `curl`:**

```bash
curl -X POST "http://localhost:8000/api/v1/kafka/webhook" \
-H "Content-Type: application/json" \
-d '{
    "id": "b3b53031-e83a-4654-87f5-b6b6fb09fd99",
    "source": "WH-3322",
    "specversion": "1.0",
    "type": "ru.retail.warehouses.movement",
    "datacontenttype": "application/json",
    "dataschema": "ru.retail.warehouses.movement.v1.0",
    "time": 1737439421623,
    "subject": "WH-3322:DEPARTURE",
    "destination": "ru.retail.warehouses",
    "data": {
        "movement_id": "c6290746-790e-43fa-8270-014dc90e02e0",
        "warehouse_id": "25718666-6af6-4281-b5a6-3016e36fa557",
        "timestamp": "2025-02-18T12:12:56Z",
        "event": "departure",
        "product_id": "4705204f-498f-4f96-b4ba-df17fb56bf55",
        "quantity": 100
    }
}'
```

### Пример сообщений Kafka (формат `data` части)

**Прибытие (`arrival`):**
```json
{
    "movement_id": "c6290746-790e-43fa-8270-014dc90e02e0",
    "warehouse_id": "c1d70455-7e14-11e9-812a-70106f431230",
    "timestamp": "2025-02-18T14:34:56Z",
    "event": "arrival",
    "product_id": "4705204f-498f-4f96-b4ba-df17fb56bf55",
    "quantity": 98
}
```

**Отбытие (`departure`):**
```json
{
    "movement_id": "c6290746-790e-43fa-8270-014dc90e02e0",
    "warehouse_id": "25718666-6af6-4281-b5a6-3016e36fa557",
    "timestamp": "2025-02-18T12:12:56Z",
    "event": "departure",
    "product_id": "4705204f-498f-4f96-b4ba-df17fb56bf55",
    "quantity": 100
}
```

## Тестирование

Для запуска тестов используется `pytest`. Тесты запускаются внутри Docker контейнера, чтобы обеспечить идентичное окружение. Используется отдельная тестовая база данных (`<POSTGRES_DB>_autotest`).

**Команда для запуска тестов:**

```bash
docker compose run --rm -e IS_AUTOTEST=True app pytest tests/
```
*   `-e IS_AUTOTEST=True`: Указывает приложению использовать тестовую конфигурацию (например, тестовую БД и `NullPool` для SQLAlchemy).
*   `--rm`: Удаляет контейнер после завершения тестов.
*   `app`: Имя сервиса из `docker-compose.yml`.
*   `pytest tests/`: Команда, выполняемая внутри контейнера.

## Структура проекта

```
.
├── app/                            # Основной код приложения
│   ├── api/                        # API эндпоинты и схемы
│   │   └── v1/
│   │       ├── endpoints/          # Логика обработки API запросов
│   │       └── schemas/            # Pydantic модели (схемы данных)
│   ├── core/                       # Базовая конфигурация, утилиты (e.g., Redis)
│   ├── db/                         # Все, что связано с БД
│   │   ├── models/                 # SQLAlchemy модели
│   │   ├── migrations/             # Alembic миграции
│   │   ├── session.py              # Настройка движка и сессий SQLAlchemy
│   │   └── base.py                 # Базовый класс для моделей
│   ├── services/                   # Бизнес-логика, обработчики
│   │   ├── kafka_processor.py      # Логика обработки Kafka сообщений
│   │   └── kafka_consumer.py       # Фоновый Kafka консьюмер
│   ├── config.py                   # Загрузка настроек (из .env)
│   └── main.py                     # Точка входа FastAPI приложения
├── tests/                          # Тесты
│   ├── api/
│   ├── services/
│   └── conftest.py                 # Настройки и фикстуры Pytest
├── alembic.ini                     # Конфигурация Alembic
├── Dockerfile                      # Инструкции для сборки Docker образа приложения
├── docker-compose.yml              # Определение сервисов для Docker Compose
├── docker-entrypoint.sh            # Скрипт инициализации контейнера (ожидание, миграции)
├── requirements.txt                # Зависимости Python
├── .env.example                    # Пример файла переменных окружения
├── .gitignore                      # Файлы, игнорируемые Git
├── .dockerignore                   # Файлы, игнорируемые Docker при сборке
└── README.md                       # <-- Вы здесь
```