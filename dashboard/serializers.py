from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    created_at_formatted = serializers.SerializerMethodField()
    order_id = serializers.CharField(source='order.id', read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'notification_type', 'is_read', 'created_at', 'created_at_formatted', 'order_id', 'order_number']

    def get_created_at_formatted(self, obj):
        from django.utils.timesince import timesince
        return f"il y a {timesince(obj.created_at)}"
