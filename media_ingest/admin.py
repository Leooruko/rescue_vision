"""
Admin configuration for media_ingest app.
"""
from django.contrib import admin
from .models import Frame


@admin.register(Frame)
class FrameAdmin(admin.ModelAdmin):
    """Admin interface for Frame model."""
    list_display = ['id', 'timestamp', 'processed', 'matched_case_id']
    list_filter = ['processed', 'timestamp']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
