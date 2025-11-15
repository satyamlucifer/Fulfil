"""
API URL routing for products app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, WebhookViewSet, ImportJobViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'webhooks', WebhookViewSet, basename='webhook')
router.register(r'import-jobs', ImportJobViewSet, basename='import-job')

urlpatterns = [
    path('', include(router.urls)),
]

