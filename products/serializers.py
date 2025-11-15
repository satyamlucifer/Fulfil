"""
Django REST Framework serializers for Product and Webhook models.
"""

from rest_framework import serializers
from .models import Product, Webhook, ImportJob


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model."""
    
    class Meta:
        model = Product
        fields = ['id', 'sku', 'name', 'description', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_sku(self, value):
        """Ensure SKU is case-insensitive unique."""
        value = value.upper()
        instance = self.instance
        
        # Check if SKU already exists (case-insensitive)
        existing = Product.objects.filter(sku=value)
        if instance:
            existing = existing.exclude(pk=instance.pk)
        
        if existing.exists():
            raise serializers.ValidationError("A product with this SKU already exists.")
        
        return value


class WebhookSerializer(serializers.ModelSerializer):
    """Serializer for Webhook model."""
    
    class Meta:
        model = Webhook
        fields = [
            'id', 'url', 'event_type', 'is_active', 'description',
            'created_at', 'updated_at', 'last_triggered_at',
            'last_response_code', 'last_response_time_ms'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'last_triggered_at',
            'last_response_code', 'last_response_time_ms'
        ]


class ImportJobSerializer(serializers.ModelSerializer):
    """Serializer for ImportJob model."""
    progress_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = ImportJob
        fields = [
            'id', 'task_id', 'filename', 'status', 'total_rows',
            'processed_rows', 'created_count', 'updated_count',
            'error_count', 'progress_percentage', 'error_message',
            'created_at', 'started_at', 'completed_at'
        ]
        read_only_fields = '__all__'

