"""
WebSocket consumers for real-time progress updates.
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer


class ImportProgressConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time CSV import progress updates.
    """
    
    async def connect(self):
        """Handle WebSocket connection."""
        self.task_id = self.scope['url_route']['kwargs']['task_id']
        self.room_group_name = f'import_{self.task_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """Handle messages from WebSocket."""
        pass

    async def import_progress(self, event):
        """
        Receive progress update from room group and send to WebSocket.
        """
        data = event['data']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'progress',
            'data': data
        }))

