"""
Django admin configuration for Product and Webhook models.
"""

from django.contrib import admin
from .models import Product, Webhook, ImportJob


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['sku', 'name', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['sku', 'name', 'description']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Webhook)
class WebhookAdmin(admin.ModelAdmin):
    list_display = ['url', 'event_type', 'is_active', 'last_triggered_at', 'last_response_code']
    list_filter = ['event_type', 'is_active']
    search_fields = ['url', 'description']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'last_triggered_at', 'last_response_code', 'last_response_time_ms']


@admin.register(ImportJob)
class ImportJobAdmin(admin.ModelAdmin):
    list_display = ['task_id', 'filename', 'status', 'progress_percentage', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['task_id', 'filename']
    ordering = ['-created_at']
    readonly_fields = ['task_id', 'created_at', 'started_at', 'completed_at']

