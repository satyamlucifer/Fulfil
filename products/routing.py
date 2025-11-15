"""
WebSocket URL routing.
"""

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/import/(?P<task_id>[^/]+)/$', consumers.ImportProgressConsumer.as_asgi()),
]

