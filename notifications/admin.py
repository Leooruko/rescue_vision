"""
Admin configuration for notifications app.
"""
from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin interface for Notification model."""
    list_display = ['missing_person', 'user', 'status', 'detection_timestamp', 'created_at']
    list_filter = ['status', 'created_at', 'detection_timestamp']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
