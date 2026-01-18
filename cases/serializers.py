"""
Serializers for cases app.
"""
from rest_framework import serializers
from .models import MissingPerson, MissingPersonImage


class MissingPersonImageSerializer(serializers.ModelSerializer):
    """Serializer for MissingPersonImage."""
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = MissingPersonImage
        fields = ['id', 'image', 'image_url', 'embedding_reference', 'created_at']
        read_only_fields = ['id', 'embedding_reference', 'created_at']
    
    def get_image_url(self, obj):
        """Get full URL for image."""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class MissingPersonSerializer(serializers.ModelSerializer):
    """Serializer for MissingPerson."""
    images = MissingPersonImageSerializer(many=True, read_only=True)
    reporter_name = serializers.CharField(source='reporter.username', read_only=True)
    reporter_email = serializers.CharField(source='reporter.email', read_only=True)
    reporter_phone = serializers.CharField(source='reporter.phone_number', read_only=True)
    
    class Meta:
        model = MissingPerson
        fields = [
            'id', 'name', 'description', 'status', 'reporter',
            'reporter_name', 'reporter_email', 'reporter_phone',
            'images', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Create missing person case."""
        validated_data['reporter'] = self.context['request'].user
        return super().create(validated_data)


class MissingPersonListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""
    primary_image = serializers.SerializerMethodField()
    reporter_name = serializers.CharField(source='reporter.username', read_only=True)
    
    class Meta:
        model = MissingPerson
        fields = [
            'id', 'name', 'status', 'primary_image',
            'reporter_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_primary_image(self, obj):
        """Get first image URL if available."""
        first_image = obj.images.first()
        if first_image and first_image.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(first_image.image.url)
            return first_image.image.url
        return None
