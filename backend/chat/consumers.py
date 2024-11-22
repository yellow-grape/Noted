import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_id = self.scope['url_route']['kwargs']['group_id']
        self.group_name = f'chat_{self.group_id}'
        self.user = self.scope.get('user', AnonymousUser())

        # Reject connection if user is not authenticated
        if not self.user.is_authenticated:
            print(f"Rejecting connection for unauthenticated user")
            await self.close()
            return

        print(f"User {self.user.username} connecting to group {self.group_name}")

        # Join group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
        print(f"User {self.user.username} connected successfully")

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            print(f"User {self.user.username} disconnecting from group {self.group_name}")
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        if not self.user.is_authenticated:
            return

        try:
            text_data_json = json.loads(text_data)
            message = text_data_json.get('message', '')
            
            if message:
                print(f"Received message from {self.user.username}: {message}")
                
                # Send message to group
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        'type': 'chat_message',
                        'message': message,
                        'user': self.user.username,
                    }
                )
        except json.JSONDecodeError:
            print(f"Invalid message format received: {text_data}")

    async def chat_message(self, event):
        message = event['message']
        user = event['user']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': message,
            'user': user,
        }))
