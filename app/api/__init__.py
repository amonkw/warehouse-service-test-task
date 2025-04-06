# Собираем все роутеры API в одном месте для удобного импорта в app/__init__.py
from .v1.endpoints import movements, stock, kafka

routers = [
    movements.router,
    stock.router,
    kafka.router
]

__all__ = ['routers']