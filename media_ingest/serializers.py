"""
Serializers for media_ingest app.
"""
from rest_framework import serializers
from .models import Frame


class FrameSerializer(serializers.ModelSerializer):
    """Serializer for Frame model."""
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Frame
        fields = ['id', 'image', 'image_url', 'timestamp', 'processed', 'matched_case_id']
        read_only_fields = ['id', 'timestamp', 'processed', 'matched_case_id']
    
    def get_image_url(self, obj):
        """Get full URL for image."""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class FrameIngestSerializer(serializers.ModelSerializer):
    """Serializer for frame ingestion from Raspberry Pi."""
    
    class Meta:
        model = Frame
        fields = ['image']
    
    def create(self, validated_data):
        """Create frame instance."""
        return Frame.objects.create(**validated_data)
