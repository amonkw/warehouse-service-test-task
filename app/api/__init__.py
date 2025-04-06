from .v1.endpoints import movements, stock, kafka_webhook

routers = [movements.router, stock.router, kafka_webhook.router]

__all__ = ["routers"]
