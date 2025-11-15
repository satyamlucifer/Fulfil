"""
Celery tasks for async processing of CSV imports and webhook triggers.
"""

import csv
import time
from celery import shared_task
from django.utils import timezone
from django.db import transaction
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import requests
import logging

from .models import Product, Webhook, ImportJob

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def process_csv_import(self, csv_content, filename, task_id):
    """
    Process CSV content and import products.
    Updates progress via WebSocket.
    """
    channel_layer = get_channel_layer()
    
    try:
        # Get or create import job
        import_job, created = ImportJob.objects.get_or_create(
            task_id=task_id,
            defaults={
                'filename': filename,
                'status': 'processing',
                'started_at': timezone.now()
            }
        )
        
        if not created:
            import_job.status = 'processing'
            import_job.started_at = timezone.now()
            import_job.save()

        # Trigger bulk import started webhook
        trigger_webhook_sync('bulk_import_started', {
            'task_id': task_id,
            'filename': filename
        })

        # First pass: count total rows
        lines = csv_content.strip().split('\n')
        reader = csv.DictReader(lines)
        total_rows = sum(1 for row in reader)
        
        import_job.total_rows = total_rows
        import_job.save()

        # Send initial progress
        async_to_sync(channel_layer.group_send)(
            f'import_{task_id}',
            {
                'type': 'import_progress',
                'data': {
                    'task_id': task_id,
                    'status': 'processing',
                    'total_rows': total_rows,
                    'processed_rows': 0,
                    'progress': 0,
                    'created_count': 0,
                    'updated_count': 0,
                    'error_count': 0,
                }
            }
        )

        # Second pass: process rows in batches
        batch_size = 1000
        processed_rows = 0
        created_count = 0
        updated_count = 0
        error_count = 0

        lines = csv_content.strip().split('\n')
        reader = csv.DictReader(lines)
        batch = []

        for row in reader:
            try:
                # Normalize column names (strip whitespace, lowercase)
                row = {k.strip().lower(): v.strip() if v else '' for k, v in row.items()}
                
                # Extract fields (assuming CSV has: sku, name, description)
                sku = row.get('sku', '').upper()
                name = row.get('name', '')
                description = row.get('description', '')

                if not sku or not name:
                    error_count += 1
                    continue

                batch.append({
                    'sku': sku,
                    'name': name,
                    'description': description,
                })

                if len(batch) >= batch_size:
                    created, updated, errors = process_batch(batch)
                    created_count += created
                    updated_count += updated
                    error_count += errors
                    processed_rows += len(batch)
                    batch = []

                    # Update progress
                    progress = round((processed_rows / total_rows) * 100, 2)
                    
                    import_job.processed_rows = processed_rows
                    import_job.created_count = created_count
                    import_job.updated_count = updated_count
                    import_job.error_count = error_count
                    import_job.save()

                    # Send progress update via WebSocket
                    async_to_sync(channel_layer.group_send)(
                        f'import_{task_id}',
                        {
                            'type': 'import_progress',
                            'data': {
                                'task_id': task_id,
                                'status': 'processing',
                                'total_rows': total_rows,
                                'processed_rows': processed_rows,
                                'progress': progress,
                                'created_count': created_count,
                                'updated_count': updated_count,
                                'error_count': error_count,
                            }
                        }
                    )

            except Exception as e:
                logger.error(f"Error processing row: {e}")
                error_count += 1

        # Process remaining batch
        if batch:
            created, updated, errors = process_batch(batch)
            created_count += created
            updated_count += updated
            error_count += errors
            processed_rows += len(batch)

        # Mark as completed
        import_job.status = 'completed'
        import_job.processed_rows = processed_rows
        import_job.created_count = created_count
        import_job.updated_count = updated_count
        import_job.error_count = error_count
        import_job.completed_at = timezone.now()
        import_job.save()

        # Send final progress
        async_to_sync(channel_layer.group_send)(
            f'import_{task_id}',
            {
                'type': 'import_progress',
                'data': {
                    'task_id': task_id,
                    'status': 'completed',
                    'total_rows': total_rows,
                    'processed_rows': processed_rows,
                    'progress': 100,
                    'created_count': created_count,
                    'updated_count': updated_count,
                    'error_count': error_count,
                }
            }
        )

        # Trigger bulk import completed webhook
        trigger_webhook_sync('bulk_import_completed', {
            'task_id': task_id,
            'filename': filename,
            'total_rows': total_rows,
            'created_count': created_count,
            'updated_count': updated_count,
            'error_count': error_count,
        })

        return {
            'status': 'completed',
            'processed_rows': processed_rows,
            'created_count': created_count,
            'updated_count': updated_count,
            'error_count': error_count,
        }

    except Exception as e:
        logger.error(f"Error in CSV import task: {e}")
        
        # Mark as failed
        import_job.status = 'failed'
        import_job.error_message = str(e)
        import_job.completed_at = timezone.now()
        import_job.save()

        # Send error via WebSocket
        async_to_sync(channel_layer.group_send)(
            f'import_{task_id}',
            {
                'type': 'import_progress',
                'data': {
                    'task_id': task_id,
                    'status': 'failed',
                    'error_message': str(e),
                }
            }
        )

        raise


def process_batch(batch):
    """Process a batch of products using bulk operations."""
    created_count = 0
    updated_count = 0
    error_count = 0

    try:
        with transaction.atomic():
            for item in batch:
                try:
                    product, created = Product.objects.update_or_create(
                        sku=item['sku'],
                        defaults={
                            'name': item['name'],
                            'description': item['description'],
                        }
                    )
                    
                    if created:
                        created_count += 1
                        # Trigger webhook for product creation
                        trigger_webhook_sync('product_created', {
                            'id': product.id,
                            'sku': product.sku,
                            'name': product.name,
                        })
                    else:
                        updated_count += 1
                        # Trigger webhook for product update
                        trigger_webhook_sync('product_updated', {
                            'id': product.id,
                            'sku': product.sku,
                            'name': product.name,
                        })
                        
                except Exception as e:
                    logger.error(f"Error processing product {item.get('sku')}: {e}")
                    error_count += 1

    except Exception as e:
        logger.error(f"Error in batch processing: {e}")
        error_count += len(batch)

    return created_count, updated_count, error_count


@shared_task
def trigger_webhook(event_type, payload):
    """
    Trigger all active webhooks for a specific event type.
    """
    trigger_webhook_sync(event_type, payload)


def trigger_webhook_sync(event_type, payload):
    """
    Synchronous version of webhook trigger.
    """
    webhooks = Webhook.objects.filter(event_type=event_type, is_active=True)
    
    for webhook in webhooks:
        try:
            start_time = time.time()
            
            response = requests.post(
                webhook.url,
                json=payload,
                timeout=10,
                headers={'Content-Type': 'application/json'}
            )
            
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000
            
            webhook.last_triggered_at = timezone.now()
            webhook.last_response_code = response.status_code
            webhook.last_response_time_ms = response_time_ms
            webhook.save()
            
            logger.info(
                f"Webhook triggered: {webhook.url} - "
                f"Status: {response.status_code} - "
                f"Time: {response_time_ms:.2f}ms"
            )
            
        except Exception as e:
            logger.error(f"Error triggering webhook {webhook.url}: {e}")
            webhook.last_triggered_at = timezone.now()
            webhook.last_response_code = 0
            webhook.save()

