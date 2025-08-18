from rest_framework import serializers
from .models import Notification
from users.serializers import UserSerializer


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model"""
    recipient_detail = UserSerializer(source='recipient', read_only=True)
    sender_detail = UserSerializer(source='sender', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'recipient_detail', 'sender', 'sender_detail',
            'type', 'priority', 'title', 'message', 'link', 'is_read',
            'read_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'read_at']