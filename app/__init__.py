"""
Warehouse Movement Service

Микросервис для обработки перемещений товаров между складами.

Основные функции:
- Прием сообщений из Kafka о перемещениях
- Учет текущего состояния складов
- Предоставление API для работы с данными
"""

import logging

from app.config import settings
from app.main import (  # noqa: F401
    app,
    create_db,
)

logging.basicConfig(level=logging.DEBUG if settings.DEBUG else logging.INFO)
