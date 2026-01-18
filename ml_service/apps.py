"""
App configuration for ml_service.
"""
from django.apps import AppConfig


class MlServiceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ml_service'
    
    def ready(self):
        """Initialize ML service when app is ready."""
        # This can be used to pre-load models if needed
        pass
