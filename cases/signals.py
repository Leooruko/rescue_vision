"""
Signals for cases app.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import MissingPerson
from ml_service.services import MLService


@receiver(post_save, sender=MissingPerson)
def handle_case_status_change(sender, instance, **kwargs):
    """Handle case status changes - clean up embeddings when closed."""
    if instance.status == 'CLOSED':
        ml_service = MLService()
        ml_service.remove_case_embeddings(instance.id)
