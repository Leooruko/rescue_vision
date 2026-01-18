"""
App configuration for cases.
"""
from django.apps import AppConfig


class CasesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cases'
    
    def ready(self):
        """Import signals when app is ready."""
        import cases.signals
