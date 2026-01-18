"""
Views for cases app.
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import models
from .models import MissingPerson, MissingPersonImage
from .serializers import (
    MissingPersonSerializer,
    MissingPersonListSerializer,
    MissingPersonImageSerializer
)
from ml_service.services import MLService


class MissingPersonViewSet(viewsets.ModelViewSet):
    """ViewSet for MissingPerson CRUD operations."""
    queryset = MissingPerson.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return MissingPersonListSerializer
        return MissingPersonSerializer
    
    def get_queryset(self):
        """Filter queryset based on user permissions."""
        queryset = MissingPerson.objects.all()
        
        # Filter by status if provided
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by search query
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                models.Q(name__icontains=search) |
                models.Q(description__icontains=search)
            )
        
        return queryset
    
    def perform_create(self, serializer):
        """Set reporter when creating a case."""
        serializer.save(reporter=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my(self, request):
        """Get cases reported by current user."""
        queryset = self.get_queryset().filter(reporter=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """Close a missing person case."""
        case = self.get_object()
        
        # Check permission
        if case.reporter != request.user:
            return Response(
                {'error': 'You do not have permission to close this case.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        case.close()
        serializer = self.get_serializer(case)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def images(self, request, pk=None):
        """Upload an image for a missing person."""
        case = self.get_object()
        
        # Check permission
        if case.reporter != request.user:
            return Response(
                {'error': 'You do not have permission to add images to this case.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if case is active
        if case.status != 'ACTIVE':
            return Response(
                {'error': 'Cannot add images to a closed case.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = MissingPersonImageSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        image_instance = serializer.save(missing_person=case)
        
        # Process image with ML service
        try:
            ml_service = MLService()
            embedding_ref = ml_service.process_missing_person_image(
                image_instance.image.path,
                str(case.id)
            )
            image_instance.embedding_reference = embedding_ref
            image_instance.save()
        except Exception as e:
            # Log error but don't fail the request
            import logging
            logger = logging.getLogger('ml_service')
            logger.error(f"Error processing image: {str(e)}")
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
