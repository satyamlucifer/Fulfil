"""
Frontend URL routing.
"""

from django.urls import path
from .frontend_views import index

urlpatterns = [
    path('', index, name='index'),
]

