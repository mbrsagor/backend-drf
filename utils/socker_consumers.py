import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from user.models import User
from .models import Chat, GroupChat, GroupMessage
from .serializers.chat_serializer import GroupMessageSerializer, ChatWithAttachmentSerializer


class ChatConsumer(AsyncWebsocketConsumer):
    # Connect to WebSocket
    async def connect(self):
        self.user = self.scope['user']

        # Reject connection if user is not authenticated
        if not self.user.is_authenticated:
            await self.close()
            return

        # Use user-specific group: "user_{user_id}"
        self.room_group_name = f'user_{self.user.id}'

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        
        # Mark user as online in Redis
        await self.set_user_online(True)

        # Join group chats
        groups = await self.get_user_groups()
        for group_id in groups:
            await self.channel_layer.group_add(f"group_{group_id}", self.channel_name)

    # Disconnect
    async def disconnect(self, close_code):
        # Mark user as offline in Redis
        if hasattr(self, 'user') and self.user.is_authenticated:
            await self.set_user_online(False)
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type', 'message') # Default to 'message'
        
        # Handle Typing Indicator
        if message_type == 'typing':
            receiver_id = data.get('receiver_id')
            group_id = data.get('group_id')
            
            if receiver_id:
                # Send to the receiver's personal group
                await self.channel_layer.group_send(
                    f'user_{receiver_id}',
                    {
                        'type': 'user_typing',
                        'user_id': self.user.id
                    }
                )
            elif group_id:
                 # Send to the group channel
                await self.channel_layer.group_send(
                    f'group_{group_id}',
                    {
                        'type': 'user_typing',
                        'user_id': self.user.id,
                        'group_id': group_id
                    }
                )
            return

        # Handle Read Receipts
        if message_type == 'read_messages':
            sender_id = data.get('sender_id')
            if sender_id:
                await self.mark_messages_as_read(sender_id)
                # Notify the sender that their messages were read
                await self.channel_layer.group_send(
                    f'user_{sender_id}',
                    {
                        'type': 'messages_read',
                        'user_id': self.user.id, # Who read the messages
                        'sender_id': sender_id   # Whose messages were read
                    }
                )
                # Also notify the current user (reader) to update UI if needed
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'messages_read',
                        'user_id': self.user.id,
                        'sender_id': sender_id
                    }
                )
            return

        # Handle Group Message
        if message_type == 'group_message':
             group_id = data.get('group_id')
             message = data.get('message')
             attachment = data.get('attachment')

             if group_id and (message or attachment):
                 saved_msg = await self.save_group_message(group_id, message, attachment)
                 if saved_msg:
                     # If saved via serializer, saved_msg might be the instance itself
                     # But we need to handle if save_group_message returns the instance or None
                     
                     # Check if attachment exists and get URL
                     attachment_url = ""
                     if saved_msg.attachment:
                         attachment_url = saved_msg.attachment.url

                     await self.channel_layer.group_send(
                         f"group_{group_id}",
                         {
                             'type': 'group_chat_message',
                             'message': saved_msg.message, # Use saved message in case of data processing
                             'group_id': group_id,
                             'sender_id': self.user.id,
                             'sender_name': self.user.fullname,
                             'sender_avatar': await self.get_user_avatar(self.user),
                             'attachment': attachment_url,
                             'timestamp': str(saved_msg.created_at)
                         }
                     )
             return

        # Handle Chat Message
        message = data.get('message')
        receiver_id = data.get('receiver_id')
        attachment = data.get('attachment')
        
        if (not message and not attachment) or not receiver_id:
            return

        # Save message to database
        saved_chat = await self.save_message(self.user.id, receiver_id, message, attachment)
        if saved_chat:
            attachment_url = ""
            if saved_chat.attachment:
                attachment_url = saved_chat.attachment.url

            message_packet = {
                'type': 'chat_message',
                'message': saved_chat.message,
                'username': self.user.fullname, # Or username
                'sender_id': self.user.id,
                'timestamp': str(saved_chat.created_at),
                'attachment': attachment_url,
                'is_read': False
            }

            # Send to receiver
            await self.channel_layer.group_send(
                f'user_{receiver_id}',
                message_packet
            )
            
            # Send back to sender (echo) so it appears in their UI
            await self.channel_layer.group_send(
                self.room_group_name,
                message_packet
            )

    # Receive message from room group
    async def chat_message(self, event):
        # Avoid duplicate message for the sender
        if self.user.id == event.get('sender_id'):
            return

        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username'],
            'sender_id': event.get('sender_id'),
            'timestamp': event.get('timestamp'),
            'attachment': event.get('attachment'),
            'is_read': event.get('is_read', False)
        }))

    async def user_typing(self, event):
        # Don't send typing indicator to self
        if self.user.id == event['user_id']:
            return

        response = {
            'type': 'typing',
            'user_id': event['user_id']
        }
        if 'group_id' in event:
            response['group_id'] = event['group_id']

        await self.send(text_data=json.dumps(response))

    async def messages_read(self, event):
        await self.send(text_data=json.dumps({
            'type': 'read_receipt',
            'user_id': event['user_id'],
            'sender_id': event['sender_id']
        }))

    # Group chat message
    async def group_chat_message(self, event):
        # Avoid duplicate message for the sender
        if self.user.id == event['sender_id']:
            return

        await self.send(text_data=json.dumps({
            'type': 'group_message',
            'message': event['message'],
            'group_id': event['group_id'],
            'sender_id': event['sender_id'],
            'sender_name': event['sender_name'],
            'sender_avatar': event['sender_avatar'],
            'attachment': event.get('attachment'),
            'timestamp': event['timestamp']
        }))
    
    # Set user online
    @database_sync_to_async
    def set_user_online(self, is_online):
        # Prevent "NoneType" error for unauthenticated users
        if not self.user.is_authenticated:
            return

        # We use a Redis set to track online users
        # Key: "online_users"
        # Member: user_id
        from django_redis import get_redis_connection
        con = get_redis_connection("default")
        if is_online:
            con.sadd("online_users", self.user.id)
        else:
            con.srem("online_users", self.user.id)

    # Mark messages as read
    @database_sync_to_async
    def mark_messages_as_read(self, sender_id):
        # Mark all unread messages from sender_id to current user as read
        Chat.objects.filter(
            sender_id=sender_id, 
            receiver=self.user, 
            is_read=False
        ).update(is_read=True)

    # Save message to database
    @database_sync_to_async
    def save_message(self, sender_id, receiver_id, message, attachment=None):
        try:
            data = {
                'receiver': receiver_id,
                'message': message if message else "",
            }
            if attachment:
                data['attachment'] = attachment

            serializer = ChatWithAttachmentSerializer(data=data)
            if serializer.is_valid():
                # Manually set sender since it's read-only
                return serializer.save(sender_id=sender_id)
            else:
                print(f"Chat Serializer errors: {serializer.errors}")
                return None
        except Exception as e:
            # Log the error here if logging is configured
            print(f"Error saving message: {e}") 
            return None

    # Get user groups
    @database_sync_to_async
    def get_user_groups(self):
        if not self.user.is_authenticated:
            return []
        return list(self.user.group_chats.values_list('id', flat=True))

    # Save group message to database
    @database_sync_to_async
    def save_group_message(self, group_id, message, attachment=None):
         try:
             # Just checking if group and user are valid
             group = GroupChat.objects.get(id=group_id)
             if self.user not in group.members.all():
                 return None

             data = {
                 'group': group_id,
                 'sender': self.user.id,
                 'message': message if message else "",
             }
             if attachment:
                 data['attachment'] = attachment
                 # print(f"DEBUG: Attachment length: {len(str(attachment))}") # Debug log

             serializer = GroupMessageSerializer(data=data)
             if serializer.is_valid():
                return serializer.save(sender=self.user)
             else:
                #  print(f"Serializer errors: {serializer.errors}")
                #  print(f"Data keys: {data.keys()}") 
                 return None
         except Exception as e:
             print(f"Error saving group message: {e}")
         return None

    # Get user avatar
    @database_sync_to_async
    def get_user_avatar(self, user):
        try:
            if hasattr(user, 'profile') and user.profile.avatar:
                return user.profile.avatar.url
            return ""
        except Exception:
            return ""
 
