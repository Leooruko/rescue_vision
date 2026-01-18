"""
Serializers for notifications app.
"""
from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model."""
    matched_image_url = serializers.SerializerMethodField()
    missing_person_name = serializers.CharField(source='missing_person.name', read_only=True)
    missing_person_id = serializers.UUIDField(source='missing_person.id', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'missing_person', 'missing_person_name', 'missing_person_id',
            'message', 'matched_image', 'matched_image_url', 'status',
            'detection_timestamp', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']
    
    def get_matched_image_url(self, obj):
        """Get full URL for matched image."""
        if obj.matched_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.matched_image.url)
            return obj.matched_image.url
        return None
