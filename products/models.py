"""
Django models for Product and Webhook.
"""

from django.db import models
from django.utils import timezone


class Product(models.Model):
    """
    Product model with case-insensitive unique SKU.
    """
    # Case-insensitive unique SKU
    sku = models.CharField(max_length=255, unique=True, db_index=True)
    name = models.CharField(max_length=500)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True, db_index=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['is_active']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.sku} - {self.name}"

    def save(self, *args, **kwargs):
        """Ensure SKU is stored in uppercase for case-insensitive uniqueness."""
        if self.sku:
            self.sku = self.sku.upper()
        super().save(*args, **kwargs)


class Webhook(models.Model):
    """
    Webhook configuration model for triggering external URLs.
    """
    EVENT_CHOICES = [
        ('product_created', 'Product Created'),
        ('product_updated', 'Product Updated'),
        ('product_deleted', 'Product Deleted'),
        ('bulk_import_started', 'Bulk Import Started'),
        ('bulk_import_completed', 'Bulk Import Completed'),
        ('bulk_delete_completed', 'Bulk Delete Completed'),
    ]

    url = models.URLField(max_length=500)
    event_type = models.CharField(max_length=50, choices=EVENT_CHOICES)
    is_active = models.BooleanField(default=True, db_index=True)
    description = models.TextField(blank=True, null=True)
    
    # Webhook metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_triggered_at = models.DateTimeField(null=True, blank=True)
    last_response_code = models.IntegerField(null=True, blank=True)
    last_response_time_ms = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = 'webhooks'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['event_type', 'is_active']),
        ]

    def __str__(self):
        return f"{self.event_type} - {self.url}"


class ImportJob(models.Model):
    """
    Track CSV import jobs for progress monitoring.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    task_id = models.CharField(max_length=255, unique=True, db_index=True)
    filename = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    total_rows = models.IntegerField(default=0)
    processed_rows = models.IntegerField(default=0)
    created_count = models.IntegerField(default=0)
    updated_count = models.IntegerField(default=0)
    error_count = models.IntegerField(default=0)
    
    error_message = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'import_jobs'
        ordering = ['-created_at']

    def __str__(self):
        return f"Import Job {self.task_id} - {self.status}"

    @property
    def progress_percentage(self):
        """Calculate progress percentage."""
        if self.total_rows == 0:
            return 0
        return round((self.processed_rows / self.total_rows) * 100, 2)

