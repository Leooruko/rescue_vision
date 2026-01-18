"""
URLs for media_ingest app.
"""
from django.urls import path
from .views import ready_view, ingest_view

app_name = 'media_ingest'

urlpatterns = [
    path('ready/', ready_view, name='ready'),
    path('ingest/', ingest_view, name='ingest'),
]
