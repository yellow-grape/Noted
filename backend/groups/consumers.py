import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Group, Message
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

User = get_user_model()

@database_sync_to_async
def get_group_member(group_id, user):
    if isinstance(user, AnonymousUser):
        return None
    try:
        return Group.objects.filter(id=group_id, members=user).first()
    except Group.DoesNotExist:
        return None

@database_sync_to_async
def save_message(group_id, user_id, content):
    group = Group.objects.get(id=group_id)
    user = User.objects.get(id=user_id)
    return Message.objects.create(group=group, sender=user, content=content)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_id = self.scope['url_route']['kwargs']['group_id']
        self.room_group_name = f'chat_{self.group_id}'
        self.user = self.scope["user"]

        # Check if user is authenticated and a member of the group
        group = await get_group_member(self.group_id, self.user)
        if not group:
            await self.close()
            return

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        if isinstance(self.user, AnonymousUser):
            await self.close()
            return

        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Save message to database
        saved_message = await save_message(self.group_id, self.user.id, message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'user_id': self.user.id,
                'username': self.user.username,
                'timestamp': saved_message.created_at.isoformat()
            }
        )

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'user_id': event['user_id'],
            'username': event['username'],
            'timestamp': event['timestamp']
        }))
