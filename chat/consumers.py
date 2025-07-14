import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from accounts.models import User
from .models import Conversation, Message, MessageRead

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.conversation_group_name = f'chat_{self.conversation_id}'
        self.user = self.scope['user']
        
        logger.info(f"WebSocket connection attempt for conversation {self.conversation_id} by user {self.user}")
        
        # Check if user is authenticated
        if self.user == AnonymousUser() or not self.user.is_authenticated:
            logger.warning(f"Unauthenticated user tried to connect to conversation {self.conversation_id}")
            await self.close(code=4001)
            return
        
        # Check if user is participant in conversation
        try:
            is_participant = await self.check_conversation_participant()
            if not is_participant:
                logger.warning(f"User {self.user.id} is not a participant in conversation {self.conversation_id}")
                await self.close(code=4003)
                return
        except Exception as e:
            logger.error(f"Error checking conversation participant: {e}")
            await self.close(code=4500)
            return
        
        # Join conversation group
        await self.channel_layer.group_add(
            self.conversation_group_name,
            self.channel_name
        )
        
        await self.accept()
        logger.info(f"WebSocket connected successfully for user {self.user.id} in conversation {self.conversation_id}")
        
        # Update user status
        await self.update_user_status(True)
        
        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected to chat successfully'
        }))

    async def disconnect(self, close_code):
        logger.info(f"WebSocket disconnecting for user {getattr(self.user, 'id', 'unknown')} with code {close_code}")
        
        # Leave conversation group
        if hasattr(self, 'conversation_group_name'):
            await self.channel_layer.group_discard(
                self.conversation_group_name,
                self.channel_name
            )
        
        # Update user status
        if hasattr(self, 'user') and self.user != AnonymousUser():
            try:
                await self.update_user_status(False)
            except Exception as e:
                logger.error(f"Error updating user status on disconnect: {e}")

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')
            
            logger.debug(f"Received message type: {message_type} from user {self.user.id}")
            
            if message_type == 'chat_message':
                await self.handle_chat_message(text_data_json)
            elif message_type == 'typing':
                await self.handle_typing(text_data_json)
            elif message_type == 'mark_read':
                await self.handle_mark_read(text_data_json)
            elif message_type == 'ping':
                await self.send(text_data=json.dumps({'type': 'pong'}))
            elif message_type == 'mark_read':
                await self.handle_mark_read(text_data_json)
            elif message_type == 'ping':
                await self.send(text_data=json.dumps({'type': 'pong'}))
            else:
                logger.warning(f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON received: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid message format'
            }))
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Error processing message'
            }))
    @database_sync_to_async
    def save_message(self, content):
        try:
            from django.db import transaction
            
            with transaction.atomic():
                conversation = Conversation.objects.get(id=self.conversation_id)
                
                # Create message with emoji conversion
                message = Message(
                    conversation=conversation,
                    sender=self.user,
                    content=content,
                    message_type='text'
                )
                
                # Handle emoji conversion safely
                if content:
                    try:
                        message.emoji_content = message.convert_text_to_emojis(content)
                    except Exception as e:
                        logger.error(f"Error converting text to emojis: {e}")
                        message.emoji_content = content
                
                # Save message
                message.save()
                
                # Update conversation timestamp separately
                conversation.updated_at = message.timestamp
                conversation.save(update_fields=['updated_at'])
                
                # Refresh to get all fields
                message.refresh_from_db()
                return message
                
        except Conversation.DoesNotExist:
            logger.error(f"Conversation {self.conversation_id} does not exist")
            return None
        except Exception as e:
            logger.error(f"Error saving message: {e}")
            return None
    #@database_sync_to_async    
    async def handle_chat_message(self, text_data_json):
        try:
            content = text_data_json.get('content', '').strip()
            client_message_id = text_data_json.get('client_message_id')  # For tracking
            
            if not content:
                await self.send(text_data=json.dumps({
                    'type': 'message_error',
                    'client_message_id': client_message_id,
                    'error': 'Message content cannot be empty'
                }))
                return
            
            if len(content) > 500:
                await self.send(text_data=json.dumps({
                    'type': 'message_error',
                    'client_message_id': client_message_id,
                    'error': 'Message too long (max 500 characters)'
                }))
                return
            
            # Send immediate confirmation to sender
            await self.send(text_data=json.dumps({
                'type': 'message_sending',
                'client_message_id': client_message_id,
                'status': 'sending'
            }))
            
            # Save message to database
            message = await self.save_message(content)
            
            if not message:
                await self.send(text_data=json.dumps({
                    'type': 'message_error',
                    'client_message_id': client_message_id,
                    'error': 'Failed to save message'
                }))
                return
            
            # Prepare message data
            message_data = {
                'id': str(message.id),
                'content': message.content,
                'emoji_content': message.emoji_content,
                'sender_id': str(message.sender.id),
                'sender_name': message.sender.full_name,
                'sender_avatar': message.sender.avatar_url,
                'timestamp': message.timestamp.isoformat(),
                'client_message_id': client_message_id
            }
            
            # Send to conversation group (broadcast to all participants)
            await self.channel_layer.group_send(
                self.conversation_group_name,
                {
                    'type': 'chat_message_broadcast',
                    'message_data': message_data,
                    'sender_channel': self.channel_name
                }
            )
            
            logger.info(f"Message sent successfully: {message.id} by user {self.user.id}")
            
        except Exception as e:
            logger.error(f"Error handling chat message: {e}")
            await self.send(text_data=json.dumps({
                'type': 'message_error',
                'client_message_id': client_message_id,
                'error': 'Failed to process message'
            }))
    async def chat_message_broadcast(self, event):
        """Broadcast message to all participants in the conversation"""
        try:
            message_data = event['message_data']
            sender_channel = event.get('sender_channel')
            
            # Determine if this is the sender's own message
            is_own_message = sender_channel == self.channel_name
            message_data['is_own_message'] = is_own_message
            
            # Send the message
            await self.send(text_data=json.dumps({
                'type': 'chat_message',
                'message': message_data
            }))
            
        except Exception as e:
            logger.error(f"Error broadcasting message: {e}")

    async def handle_typing(self, data):
        is_typing = data.get('is_typing', False)
        user_name = getattr(self.user, 'full_name', self.user.username)
        
        try:
            # Send typing indicator to conversation group (excluding sender)
            await self.channel_layer.group_send(
                self.conversation_group_name,
                {
                    'type': 'typing_indicator_broadcast',
                    'user_id': str(self.user.id),
                    'user_name': user_name,
                    'is_typing': is_typing,
                    'sender_channel': self.channel_name
                }
            )
        except Exception as e:
            logger.error(f"Error handling typing indicator: {e}")

    async def handle_mark_read(self, data):
        message_ids = data.get('message_ids', [])
        
        if not message_ids:
            return
        
        try:
            await self.mark_messages_read(message_ids)
            logger.debug(f"Marked {len(message_ids)} messages as read for user {self.user.id}")
        except Exception as e:
            logger.error(f"Error marking messages as read: {e}")

    # Group message handlers
    async def chat_message_broadcast(self, event):
        message = event['message']
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message
        }))

    async def typing_indicator_broadcast(self, event):
        # Don't send typing indicator back to the sender
        if event.get('sender_channel') == self.channel_name:
            return
            
        await self.send(text_data=json.dumps({
            'type': 'typing_indicator',
            'user_id': event['user_id'],
            'user_name': event['user_name'],
            'is_typing': event['is_typing']
        }))

    async def user_status_broadcast(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_status',
            'user_id': event['user_id'],
            'is_online': event['is_online']
        }))

    # Database operations
    @database_sync_to_async
    def check_conversation_participant(self):
        try:
            conversation = Conversation.objects.get(id=self.conversation_id)
            return conversation.participants.filter(id=self.user.id).exists()
        except Conversation.DoesNotExist:
            logger.error(f"Conversation {self.conversation_id} does not exist")
            return False
        except Exception as e:
            logger.error(f"Error checking conversation participant: {e}")
            return False

    @database_sync_to_async
    def update_user_status(self, is_online):
        try:
            self.user.is_online = is_online
            if not is_online:
                self.user.last_seen = timezone.now()
            self.user.save(update_fields=['is_online', 'last_seen'])
        except Exception as e:
            logger.error(f"Error updating user status: {e}")

    @database_sync_to_async
    def mark_messages_read(self, message_ids):
        try:
            messages = Message.objects.filter(
                id__in=message_ids,
                conversation_id=self.conversation_id
            ).exclude(sender=self.user)
            
            for message in messages:
                MessageRead.objects.get_or_create(
                    message=message,
                    user=self.user
                )
        except Exception as e:
            logger.error(f"Error marking messages as read: {e}")

    @database_sync_to_async
    def update_user_status(self, is_online):
        try:
            self.user.is_online = is_online
            if not is_online:
                self.user.last_seen = timezone.now()
            self.user.save(update_fields=['is_online', 'last_seen'])
        except Exception as e:
            logger.error(f"Error updating user status: {e}")


class OnlineStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        
        if self.user == AnonymousUser() or not self.user.is_authenticated:
            await self.close(code=4001)
            return
        
        self.user_group_name = f'user_{self.user.id}'
        self.general_group_name = 'online_users'
        
        # Join user-specific group
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        
        # Join general online users group
        await self.channel_layer.group_add(
            self.general_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Update user status to online
        await self.update_user_status(True)
        
        # Notify others about user coming online
        await self.broadcast_user_status(True)

    async def disconnect(self, close_code):
        # Leave groups
        if hasattr(self, 'user_group_name'):
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name
            )
        
        if hasattr(self, 'general_group_name'):
            await self.channel_layer.group_discard(
                self.general_group_name,
                self.channel_name
            )
        
        # Update user status to offline
        if hasattr(self, 'user') and self.user != AnonymousUser():
            await self.update_user_status(False)
            await self.broadcast_user_status(False)

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')
            
            if message_type == 'heartbeat':
                await self.update_user_status(True)
                await self.send(text_data=json.dumps({
                    'type': 'heartbeat_response',
                    'timestamp': timezone.now().isoformat()
                }))
            elif message_type == 'get_online_users':
                online_users = await self.get_online_friends()
                await self.send(text_data=json.dumps({
                    'type': 'online_users_list',
                    'users': online_users
                }))
        except json.JSONDecodeError:
            pass
        except Exception as e:
            logger.error(f"Error in OnlineStatusConsumer: {e}")

    async def user_status_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_status_update',
            'user_id': event['user_id'],
            'is_online': event['is_online'],
            'last_seen': event.get('last_seen')
        }))

    @database_sync_to_async
    def update_user_status(self, is_online):
        try:
            self.user.is_online = is_online
            if not is_online:
                self.user.last_seen = timezone.now()
            self.user.save(update_fields=['is_online', 'last_seen'])
        except Exception as e:
            logger.error(f"Error updating user status: {e}")

    async def broadcast_user_status(self, is_online):
        try:
            await self.channel_layer.group_send(
                self.general_group_name,
                {
                    'type': 'user_status_update',
                    'user_id': str(self.user.id),
                    'is_online': is_online,
                    'last_seen': timezone.now().isoformat() if not is_online else None
                }
            )
        except Exception as e:
            logger.error(f"Error broadcasting user status: {e}")

    @database_sync_to_async
    def get_online_friends(self):
        try:
            from accounts.models import Friendship
            friends = Friendship.get_friends(self.user)
            online_friends = []
            
            for friend in friends:
                if friend.is_online:
                    online_friends.append({
                        'id': str(friend.id),
                        'name': friend.full_name,
                        'avatar': friend.avatar_url,
                        'last_seen': friend.last_seen.isoformat()
                    })
            
            return online_friends
        except Exception as e:
            logger.error(f"Error getting online friends: {e}")
            return []