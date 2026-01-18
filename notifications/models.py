"""
Models for notifications.
"""
from django.db import models
from django.conf import settings
from cases.models import MissingPerson


class Notification(models.Model):
    """Model for detection notifications."""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('DISMISSED', 'Dismissed'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    missing_person = models.ForeignKey(
        MissingPerson,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    message = models.TextField()
    matched_image = models.ImageField(
        upload_to='detection_images/',
        help_text="Image where the match was detected"
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    detection_timestamp = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
    
    def __str__(self):
        return f"Notification for {self.missing_person.name} - {self.status}"
    
    def confirm(self):
        """Mark notification as confirmed."""
        self.status = 'CONFIRMED'
        self.save()
    
    def dismiss(self):
        """Mark notification as dismissed."""
        self.status = 'DISMISSED'
        self.save()
