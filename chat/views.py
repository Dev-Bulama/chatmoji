from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.utils import timezone
from django.core.exceptions import ValidationError
from accounts.models import User, Friendship
from .models import Conversation, Message, MessageRead
import json
import logging

logger = logging.getLogger(__name__)

@login_required
def dashboard_view(request):
    """Main chat dashboard"""
    # Update user's online status and last seen
    request.user.is_online = True
    request.user.update_last_seen()
    request.user.save(update_fields=['is_online'])
    
    # Get user's conversations
    conversations = Conversation.objects.filter(
        participants=request.user
    ).select_related('created_by').prefetch_related('participants', 'messages').order_by('-updated_at')
    
    # Prepare conversation data with other participants
    conversation_data = []
    for conversation in conversations:
        conv_data = {
            'conversation': conversation,
            'other_participant': None,
            'last_message': conversation.last_message,
        }
        
        if conversation.conversation_type == 'private':
            conv_data['other_participant'] = conversation.get_other_participant(request.user)
        
        conversation_data.append(conv_data)
    
    # Get online friends
    friends = Friendship.get_friends(request.user)
    online_friends = [friend for friend in friends if friend.is_online]
    
    # Get unread message count
    unread_count = Message.objects.filter(
        conversation__participants=request.user
    ).exclude(sender=request.user).exclude(
        read_by__user=request.user
    ).count()
    
    context = {
        'conversation_data': conversation_data,
        'conversations': conversations,  # Keep this for backward compatibility
        'online_friends': online_friends,
        'friends': friends,
        'unread_count': unread_count,
    }
    
    return render(request, 'chat/dashboard.html', context)

@login_required
def conversation_view(request, conversation_id):
    """View specific conversation"""
    conversation = get_object_or_404(
        Conversation,
        id=conversation_id,
        participants=request.user
    )
    
    # Get messages
    messages = conversation.messages.filter(is_deleted=False).select_related('sender').order_by('timestamp')
    
    # Mark messages as read
    unread_messages = messages.exclude(sender=request.user).exclude(
        read_by__user=request.user
    )
    
    for message in unread_messages:
        MessageRead.objects.get_or_create(
            message=message,
            user=request.user
        )
    
    # Get other participant for private conversations
    other_participant = None
    if conversation.conversation_type == 'private':
        other_participant = conversation.get_other_participant(request.user)
    
    context = {
        'conversation': conversation,
        'messages': messages,
        'other_participant': other_participant,
    }
    
    return render(request, 'chat/conversation.html', context)

@login_required
def start_conversation_view(request, user_id):
    """Start a conversation with a specific user"""
    other_user = get_object_or_404(User, id=user_id)
    
    # Check if they're friends
    if not Friendship.are_friends(request.user, other_user):
        messages.error(request, 'You can only start conversations with friends.')
        return redirect('accounts:user_profile', user_id=user_id)
    
    # Check if conversation already exists
    existing_conversation = Conversation.objects.filter(
        conversation_type='private',
        participants=request.user
    ).filter(participants=other_user).first()
    
    if existing_conversation:
        return redirect('chat:conversation', conversation_id=existing_conversation.id)
    
    # Create new conversation
    conversation = Conversation.objects.create(
        conversation_type='private',
        created_by=request.user
    )
    conversation.participants.add(request.user, other_user)
    
    return redirect('chat:conversation', conversation_id=conversation.id)

@login_required
@require_POST
def send_message_api(request):
    """API endpoint to send a message (fallback for non-WebSocket)"""
    try:
        # Parse JSON data
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST
        
        conversation_id = data.get('conversation_id')
        content = data.get('content', '').strip()
        
        if not conversation_id:
            return JsonResponse({'success': False, 'message': 'Conversation ID is required'})
        
        if not content:
            return JsonResponse({'success': False, 'message': 'Message content cannot be empty'})
        
        if len(content) > 500:
            return JsonResponse({'success': False, 'message': 'Message too long (max 500 characters)'})
        
        # Get conversation
        try:
            conversation = Conversation.objects.get(
                id=conversation_id,
                participants=request.user
            )
        except Conversation.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Conversation not found'})
        
        # Create message
        message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            content=content
        )
        
        # Return message data
        message_data = {
        'id': str(message.id),
        'content': message.content,
        'emoji_content': message.emoji_content or message.content,  # Ensure emoji_content exists
        'sender_id': str(message.sender.id),
        'sender_name': message.sender.full_name,
        'sender_avatar': message.sender.avatar_url,
        'timestamp': message.timestamp.isoformat(),
        'is_own_message': message.sender == request.user
}
        logger.info(f"Message sent via API: {message.id} by user {request.user.id}")
        
        return JsonResponse({
            'success': True,
            'message': message_data
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.error(f"Error sending message via API: {e}")
        return JsonResponse({'success': False, 'message': 'Failed to send message'}, status=500)

@login_required
def get_messages_api(request, conversation_id):
    """API endpoint to get messages for a conversation"""
    try:
        conversation = get_object_or_404(
            Conversation,
            id=conversation_id,
            participants=request.user
        )
        
        # Get messages with pagination
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 50))
        offset = (page - 1) * page_size
        
        messages = conversation.messages.filter(is_deleted=False).select_related('sender').order_by('-timestamp')[offset:offset + page_size]
        
        messages_data = []
        for message in reversed(messages):  # Reverse to get chronological order
            messages_data.append({
            'id': str(message.id),
            'content': message.content,
            'emoji_content': message.emoji_content or message.content,  # Ensure emoji_content exists
            'sender_id': str(message.sender.id),
            'sender_name': message.sender.full_name,
            'sender_avatar': message.sender.avatar_url,
            'timestamp': message.timestamp.isoformat(),
            'is_own_message': message.sender == request.user
})
        
        return JsonResponse({
            'messages': messages_data,
            'has_more': len(messages) == page_size
        })
        
    except Exception as e:
        logger.error(f"Error getting messages: {e}")
        return JsonResponse({'error': 'Failed to get messages'}, status=500)

@login_required
def get_online_users_api(request):
    """API endpoint to get online users"""
    try:
        friends = Friendship.get_friends(request.user)
        online_friends = []
        
        for friend in friends:
            if friend.is_online:
                online_friends.append({
                    'id': str(friend.id),
                    'name': friend.full_name,
                    'avatar': friend.avatar_url,
                    'last_seen': friend.last_seen.isoformat() if friend.last_seen else None
                })
        
        return JsonResponse({'users': online_friends})  # Changed online_users to users
        
    except Exception as e:
        logger.error(f"Error getting online users: {e}")
        return JsonResponse({'error': 'Failed to get online users'}, status=500)

@login_required
@require_POST
def update_user_status(request):
    """Update user's online status"""
    try:
        request.user.is_online = True
        request.user.update_last_seen()
        request.user.save(update_fields=['is_online', 'last_seen'])
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        logger.error(f"Error updating user status: {e}")
        return JsonResponse({'success': False, 'error': 'Failed to update status'}, status=500)

@login_required
@require_POST
def mark_messages_read_api(request):
    """API endpoint to mark messages as read"""
    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST
        
        message_ids = data.get('message_ids', [])
        conversation_id = data.get('conversation_id')
        
        if not message_ids or not conversation_id:
            return JsonResponse({'success': False, 'message': 'Message IDs and conversation ID are required'})
        
        # Verify conversation access
        try:
            conversation = Conversation.objects.get(
                id=conversation_id,
                participants=request.user
            )
        except Conversation.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Conversation not found'})
        
        # Mark messages as read
        messages = Message.objects.filter(
            id__in=message_ids,
            conversation=conversation
        ).exclude(sender=request.user)
        
        for message in messages:
            MessageRead.objects.get_or_create(
                message=message,
                user=request.user
            )
        
        return JsonResponse({'success': True, 'marked_count': len(messages)})
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.error(f"Error marking messages as read: {e}")
        return JsonResponse({'success': False, 'message': 'Failed to mark messages as read'}, status=500)

@login_required
def get_conversation_info_api(request, conversation_id):
    """API endpoint to get conversation information"""
    try:
        conversation = get_object_or_404(
            Conversation,
            id=conversation_id,
            participants=request.user
        )
        
        # Get other participant for private conversations
        other_participant = None
        if conversation.conversation_type == 'private':
            other_participant_obj = conversation.get_other_participant(request.user)
            if other_participant_obj:
                other_participant = {
                    'id': str(other_participant_obj.id),
                    'name': other_participant_obj.full_name,
                    'avatar': other_participant_obj.avatar_url,
                    'is_online': other_participant_obj.is_online,
                    'last_seen': other_participant_obj.last_seen.isoformat() if other_participant_obj.last_seen else None
                }
        
        # Get participants for group conversations
        participants = []
        if conversation.conversation_type == 'group':
            for participant in conversation.participants.all():
                participants.append({
                    'id': str(participant.id),
                    'name': participant.full_name,
                    'avatar': participant.avatar_url,
                    'is_online': participant.is_online
                })
        
        conversation_data = {
            'id': str(conversation.id),
            'name': conversation.name,
            'type': conversation.conversation_type,
            'created_at': conversation.created_at.isoformat(),
            'other_participant': other_participant,
            'participants': participants,
            'message_count': conversation.messages.filter(is_deleted=False).count()
        }
        
        return JsonResponse({'conversation': conversation_data})
        
    except Exception as e:
        logger.error(f"Error getting conversation info: {e}")
        return JsonResponse({'error': 'Failed to get conversation info'}, status=500)

@login_required
def search_conversations_api(request):
    """API endpoint to search conversations"""
    try:
        query = request.GET.get('q', '').strip()
        
        if not query:
            return JsonResponse({'conversations': []})
        
        conversations = Conversation.objects.filter(
            Q(name__icontains=query) |
            Q(participants__first_name__icontains=query) |
            Q(participants__last_name__icontains=query),
            participants=request.user
        ).distinct().select_related('created_by').prefetch_related('participants')[:10]
        
        conversations_data = []
        for conversation in conversations:
            # Get other participant for private conversations
            other_participant = None
            if conversation.conversation_type == 'private':
                other_participant_obj = conversation.get_other_participant(request.user)
                if other_participant_obj:
                    other_participant = {
                        'id': str(other_participant_obj.id),
                        'name': other_participant_obj.full_name,
                        'avatar': other_participant_obj.avatar_url
                    }
            
            conversations_data.append({
                'id': str(conversation.id),
                'name': conversation.name or (other_participant['name'] if other_participant else 'Group Chat'),
                'type': conversation.conversation_type,
                'other_participant': other_participant,
                'last_message': {
                    'content': conversation.last_message.content if conversation.last_message else None,
                    'timestamp': conversation.last_message.timestamp.isoformat() if conversation.last_message else None
                } if conversation.last_message else None
            })
        
        return JsonResponse({'conversations': conversations_data})
        
    except Exception as e:
        logger.error(f"Error searching conversations: {e}")
        return JsonResponse({'error': 'Failed to search conversations'}, status=500)
@login_required
@require_POST
def accept_friend_request_api(request):
    """API endpoint to accept friend request"""
    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST
        
        friend_request_id = data.get('friend_request_id')
        
        if not friend_request_id:
            return JsonResponse({'success': False, 'message': 'Friend request ID is required'})
        
        # Import here to avoid circular import
        from accounts.models import FriendRequest
        
        try:
            friend_request = FriendRequest.objects.get(
                id=friend_request_id,
                to_user=request.user,
                status='pending'
            )
        except FriendRequest.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Friend request not found or already processed'})
        
        # Accept the friend request
        friend_request.status = 'accepted'
        friend_request.save()
        
        # Create friendship
        friendship = Friendship.objects.create(
            user1=friend_request.from_user,
            user2=friend_request.to_user
        )
        
        logger.info(f"Friend request {friend_request_id} accepted by user {request.user.id}")
        
        return JsonResponse({
            'success': True,
            'message': 'Friend request accepted successfully',
            'friendship_id': str(friendship.id)
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.error(f"Error accepting friend request: {e}")
        return JsonResponse({'success': False, 'message': 'Failed to accept friend request'}, status=500)

@login_required
@require_POST
def decline_friend_request_api(request):
    """API endpoint to decline friend request"""
    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST
        
        friend_request_id = data.get('friend_request_id')
        
        if not friend_request_id:
            return JsonResponse({'success': False, 'message': 'Friend request ID is required'})
        
        # Import here to avoid circular import
        from accounts.models import FriendRequest
        
        try:
            friend_request = FriendRequest.objects.get(
                id=friend_request_id,
                to_user=request.user,
                status='pending'
            )
        except FriendRequest.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Friend request not found or already processed'})
        
        # Decline the friend request
        friend_request.status = 'declined'
        friend_request.save()
        
        logger.info(f"Friend request {friend_request_id} declined by user {request.user.id}")
        
        return JsonResponse({
            'success': True,
            'message': 'Friend request declined successfully'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.error(f"Error declining friend request: {e}")
        return JsonResponse({'success': False, 'message': 'Failed to decline friend request'}, status=500)