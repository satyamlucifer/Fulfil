"""
Tests for the products app.
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Product, Webhook, ImportJob
import io
import csv


class ProductModelTest(TestCase):
    """Test cases for Product model."""

    def test_product_creation(self):
        """Test creating a product."""
        product = Product.objects.create(
            sku='TEST001',
            name='Test Product',
            description='Test description',
            is_active=True
        )
        self.assertEqual(product.sku, 'TEST001')
        self.assertEqual(product.name, 'Test Product')
        self.assertTrue(product.is_active)

    def test_sku_case_insensitive(self):
        """Test that SKU is stored in uppercase."""
        product = Product.objects.create(
            sku='test001',
            name='Test Product'
        )
        self.assertEqual(product.sku, 'TEST001')

    def test_sku_uniqueness(self):
        """Test that SKU must be unique."""
        Product.objects.create(sku='TEST001', name='Product 1')
        
        with self.assertRaises(Exception):
            Product.objects.create(sku='TEST001', name='Product 2')


class WebhookModelTest(TestCase):
    """Test cases for Webhook model."""

    def test_webhook_creation(self):
        """Test creating a webhook."""
        webhook = Webhook.objects.create(
            url='https://example.com/webhook',
            event_type='product_created',
            is_active=True
        )
        self.assertEqual(webhook.url, 'https://example.com/webhook')
        self.assertEqual(webhook.event_type, 'product_created')
        self.assertTrue(webhook.is_active)


class ProductAPITest(APITestCase):
    """Test cases for Product API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.product = Product.objects.create(
            sku='TEST001',
            name='Test Product',
            description='Test description',
            is_active=True
        )

    def test_list_products(self):
        """Test listing products."""
        url = reverse('product-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_create_product(self):
        """Test creating a product via API."""
        url = reverse('product-list')
        data = {
            'sku': 'TEST002',
            'name': 'New Product',
            'description': 'New description',
            'is_active': True
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 2)

    def test_update_product(self):
        """Test updating a product."""
        url = reverse('product-detail', args=[self.product.id])
        data = {
            'sku': 'TEST001',
            'name': 'Updated Product',
            'description': 'Updated description',
            'is_active': False
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, 'Updated Product')
        self.assertFalse(self.product.is_active)

    def test_delete_product(self):
        """Test deleting a product."""
        url = reverse('product-detail', args=[self.product.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Product.objects.count(), 0)

    def test_filter_by_sku(self):
        """Test filtering products by SKU."""
        url = reverse('product-list')
        response = self.client.get(url, {'sku': 'TEST001'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_filter_by_active_status(self):
        """Test filtering products by active status."""
        Product.objects.create(
            sku='TEST002',
            name='Inactive Product',
            is_active=False
        )
        
        url = reverse('product-list')
        response = self.client.get(url, {'is_active': 'true'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_bulk_delete(self):
        """Test bulk delete functionality."""
        Product.objects.create(sku='TEST002', name='Product 2')
        Product.objects.create(sku='TEST003', name='Product 3')
        
        url = reverse('product-bulk-delete')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Product.objects.count(), 0)


class WebhookAPITest(APITestCase):
    """Test cases for Webhook API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.webhook = Webhook.objects.create(
            url='https://example.com/webhook',
            event_type='product_created',
            is_active=True
        )

    def test_list_webhooks(self):
        """Test listing webhooks."""
        url = reverse('webhook-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_create_webhook(self):
        """Test creating a webhook."""
        url = reverse('webhook-list')
        data = {
            'url': 'https://example.com/webhook2',
            'event_type': 'product_updated',
            'is_active': True
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Webhook.objects.count(), 2)

    def test_update_webhook(self):
        """Test updating a webhook."""
        url = reverse('webhook-detail', args=[self.webhook.id])
        data = {
            'url': 'https://example.com/updated',
            'event_type': 'product_created',
            'is_active': False
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.webhook.refresh_from_db()
        self.assertEqual(self.webhook.url, 'https://example.com/updated')

    def test_delete_webhook(self):
        """Test deleting a webhook."""
        url = reverse('webhook-detail', args=[self.webhook.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Webhook.objects.count(), 0)


class CSVUploadTest(APITestCase):
    """Test cases for CSV upload functionality."""

    def create_csv_file(self, rows):
        """Helper method to create a CSV file."""
        csv_file = io.StringIO()
        writer = csv.writer(csv_file)
        writer.writerow(['sku', 'name', 'description'])
        for row in rows:
            writer.writerow(row)
        csv_file.seek(0)
        return io.BytesIO(csv_file.getvalue().encode('utf-8'))

    def test_csv_upload_endpoint(self):
        """Test CSV upload endpoint."""
        rows = [
            ['TEST001', 'Product 1', 'Description 1'],
            ['TEST002', 'Product 2', 'Description 2'],
        ]
        csv_file = self.create_csv_file(rows)
        csv_file.name = 'test.csv'
        
        url = reverse('product-upload-csv')
        response = self.client.post(url, {'file': csv_file}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertIn('task_id', response.data)

    def test_csv_upload_no_file(self):
        """Test CSV upload without file."""
        url = reverse('product-upload-csv')
        response = self.client.post(url, {}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_csv_upload_wrong_format(self):
        """Test CSV upload with wrong file format."""
        file_content = io.BytesIO(b'Not a CSV file')
        file_content.name = 'test.txt'
        
        url = reverse('product-upload-csv')
        response = self.client.post(url, {'file': file_content}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ImportJobTest(TestCase):
    """Test cases for ImportJob model."""

    def test_import_job_creation(self):
        """Test creating an import job."""
        job = ImportJob.objects.create(
            task_id='test-task-123',
            filename='test.csv',
            status='pending'
        )
        self.assertEqual(job.task_id, 'test-task-123')
        self.assertEqual(job.status, 'pending')

    def test_progress_percentage(self):
        """Test progress percentage calculation."""
        job = ImportJob.objects.create(
            task_id='test-task-123',
            filename='test.csv',
            total_rows=100,
            processed_rows=50
        )
        self.assertEqual(job.progress_percentage, 50.0)

    def test_progress_percentage_zero_rows(self):
        """Test progress percentage with zero total rows."""
        job = ImportJob.objects.create(
            task_id='test-task-123',
            filename='test.csv',
            total_rows=0,
            processed_rows=0
        )
        self.assertEqual(job.progress_percentage, 0)

