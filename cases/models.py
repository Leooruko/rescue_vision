"""
Models for missing person cases.
"""
import uuid
from django.db import models
from django.conf import settings


class MissingPerson(models.Model):
    """Model representing a missing person case."""
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('CLOSED', 'Closed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, help_text="Additional details about the missing person")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVE')
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reported_cases'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'missing_persons'
        ordering = ['-created_at']
        verbose_name = 'Missing Person'
        verbose_name_plural = 'Missing Persons'
    
    def __str__(self):
        return f"{self.name} ({self.status})"
    
    def close(self):
        """Close the case."""
        self.status = 'CLOSED'
        self.save()


class MissingPersonImage(models.Model):
    """Model storing images of missing persons with embedding references."""
    
    missing_person = models.ForeignKey(
        MissingPerson,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='missing_person_images/')
    embedding_reference = models.CharField(
        max_length=500,
        blank=True,
        help_text="Reference to stored embedding (e.g., file path or ID)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'missing_person_images'
        ordering = ['-created_at']
        verbose_name = 'Missing Person Image'
        verbose_name_plural = 'Missing Person Images'
    
    def __str__(self):
        return f"Image for {self.missing_person.name}"
