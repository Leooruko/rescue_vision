"""
Models for media ingestion from Raspberry Pi.
"""
from django.db import models


class Frame(models.Model):
    """Model storing frames captured from Raspberry Pi camera."""
    
    image = models.ImageField(upload_to='frames/')
    timestamp = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    matched_case_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="ID of matched missing person case if detection occurred"
    )
    
    class Meta:
        db_table = 'frames'
        ordering = ['-timestamp']
        verbose_name = 'Frame'
        verbose_name_plural = 'Frames'
    
    def __str__(self):
        return f"Frame {self.id} - {self.timestamp}"
