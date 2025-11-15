"""
Django REST Framework views for Product and Webhook APIs.
"""

import os
import uuid
from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import Product, Webhook, ImportJob
from .serializers import ProductSerializer, WebhookSerializer, ImportJobSerializer
from .tasks import process_csv_import, trigger_webhook


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Product CRUD operations with filtering and pagination.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['sku', 'name', 'description']
    ordering_fields = ['created_at', 'updated_at', 'sku', 'name']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Override to support custom filtering.
        """
        queryset = super().get_queryset()
        
        # Custom filters
        sku = self.request.query_params.get('sku', None)
        name = self.request.query_params.get('name', None)
        is_active = self.request.query_params.get('is_active', None)
        
        if sku:
            queryset = queryset.filter(sku__icontains=sku)
        if name:
            queryset = queryset.filter(name__icontains=name)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
            
        return queryset

    def perform_create(self, serializer):
        """Trigger webhook on product creation."""
        product = serializer.save()
        trigger_webhook.delay('product_created', {
            'id': product.id,
            'sku': product.sku,
            'name': product.name,
        })

    def perform_update(self, serializer):
        """Trigger webhook on product update."""
        product = serializer.save()
        trigger_webhook.delay('product_updated', {
            'id': product.id,
            'sku': product.sku,
            'name': product.name,
        })

    def perform_destroy(self, instance):
        """Trigger webhook on product deletion."""
        product_data = {
            'id': instance.id,
            'sku': instance.sku,
            'name': instance.name,
        }
        instance.delete()
        trigger_webhook.delay('product_deleted', product_data)

    @action(detail=False, methods=['delete'])
    def bulk_delete(self, request):
        """
        Delete all products (STORY 3).
        """
        count = Product.objects.count()
        Product.objects.all().delete()
        
        # Trigger webhook
        trigger_webhook.delay('bulk_delete_completed', {
            'deleted_count': count,
            'timestamp': timezone.now().isoformat(),
        })
        
        return Response({
            'message': f'Successfully deleted {count} products',
            'deleted_count': count
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_csv(self, request):
        """
        Upload CSV file for bulk import (STORY 1).
        """
        if 'file' not in request.FILES:
            return Response(
                {'error': 'No file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        uploaded_file = request.FILES['file']
        
        if not uploaded_file.name.endswith('.csv'):
            return Response(
                {'error': 'File must be a CSV'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Generate unique task ID
        task_id = str(uuid.uuid4())
        
        # Save file temporarily
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, f'{task_id}_{uploaded_file.name}')
        
        with open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        # Create import job
        import_job = ImportJob.objects.create(
            task_id=task_id,
            filename=uploaded_file.name,
            status='pending'
        )

        # Start Celery task
        process_csv_import.apply_async(
            args=[file_path, uploaded_file.name, task_id],
            task_id=task_id
        )

        return Response({
            'task_id': task_id,
            'message': 'File upload started',
            'filename': uploaded_file.name,
        }, status=status.HTTP_202_ACCEPTED)

    @action(detail=False, methods=['get'])
    def import_status(self, request):
        """
        Get status of import job (STORY 1A).
        """
        task_id = request.query_params.get('task_id')
        
        if not task_id:
            return Response(
                {'error': 'task_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            import_job = ImportJob.objects.get(task_id=task_id)
            serializer = ImportJobSerializer(import_job)
            return Response(serializer.data)
        except ImportJob.DoesNotExist:
            return Response(
                {'error': 'Import job not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class WebhookViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Webhook CRUD operations (STORY 4).
    """
    queryset = Webhook.objects.all()
    serializer_class = WebhookSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['event_type', 'is_active']
    ordering_fields = ['created_at', 'event_type']
    ordering = ['-created_at']

    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """
        Test a webhook by triggering it with sample data.
        """
        webhook = self.get_object()
        
        test_payload = {
            'test': True,
            'webhook_id': webhook.id,
            'event_type': webhook.event_type,
            'timestamp': timezone.now().isoformat(),
            'message': 'This is a test webhook trigger'
        }
        
        # Trigger webhook immediately (not async for test)
        import time
        import requests
        
        try:
            start_time = time.time()
            response = requests.post(
                webhook.url,
                json=test_payload,
                timeout=10,
                headers={'Content-Type': 'application/json'}
            )
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000
            
            webhook.last_triggered_at = timezone.now()
            webhook.last_response_code = response.status_code
            webhook.last_response_time_ms = response_time_ms
            webhook.save()
            
            return Response({
                'success': True,
                'status_code': response.status_code,
                'response_time_ms': round(response_time_ms, 2),
                'message': 'Webhook tested successfully'
            })
            
        except Exception as e:
            webhook.last_triggered_at = timezone.now()
            webhook.last_response_code = 0
            webhook.save()
            
            return Response({
                'success': False,
                'error': str(e),
                'message': 'Webhook test failed'
            }, status=status.HTTP_400_BAD_REQUEST)


class ImportJobViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing import job history.
    """
    queryset = ImportJob.objects.all()
    serializer_class = ImportJobSerializer
    ordering = ['-created_at']

