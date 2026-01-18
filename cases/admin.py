"""
Admin configuration for cases app.
"""
from django.contrib import admin
from .models import MissingPerson, MissingPersonImage


class MissingPersonImageInline(admin.TabularInline):
    """Inline admin for MissingPersonImage."""
    model = MissingPersonImage
    extra = 1


@admin.register(MissingPerson)
class MissingPersonAdmin(admin.ModelAdmin):
    """Admin interface for MissingPerson model."""
    list_display = ['name', 'status', 'reporter', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    inlines = [MissingPersonImageInline]


@admin.register(MissingPersonImage)
class MissingPersonImageAdmin(admin.ModelAdmin):
    """Admin interface for MissingPersonImage model."""
    list_display = ['missing_person', 'image', 'created_at']
    list_filter = ['created_at']
    readonly_fields = ['created_at']
