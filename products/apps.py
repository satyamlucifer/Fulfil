from django.apps import AppConfig


class ProductsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'products'

    def ready(self):
        """Import Celery app to ensure tasks are registered."""
        from config import celery as celery_app
        __all__ = ('celery_app',)

