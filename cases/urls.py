"""
URLs for cases app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MissingPersonViewSet

app_name = 'cases'

router = DefaultRouter()
router.register(r'', MissingPersonViewSet, basename='missingperson')

urlpatterns = [
    path('', include(router.urls)),
]
