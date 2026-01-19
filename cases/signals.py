"""
Signals for cases app.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import MissingPerson
import logging

logger = logging.getLogger('cases')


@receiver(post_save, sender=MissingPerson)
def handle_case_status_change(sender, instance, **kwargs):
    """Handle case status changes - clean up face crops when closed."""
    if instance.status == 'CLOSED':
        try:
            from ml_service.services import MLService
            ml_service = MLService()
            ml_service.remove_case_embeddings(instance.id)
        except Exception as e:
            # Log error but don't fail the signal if ML service is unavailable
            logger.warning(f"Failed to clean up face crops for case {instance.id}: {str(e)}")
