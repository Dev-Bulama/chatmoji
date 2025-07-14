from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.exceptions import ValidationError
from .models import User, FriendRequest, Friendship
from .forms import CustomUserCreationForm, CustomAuthenticationForm, ProfileUpdateForm
import json
import logging

logger = logging.getLogger(__name__)

def register_view(request):
    if request.user.is_authenticated:
        return redirect('chat:dashboard')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully! Welcome to ChatMoji!')
            return redirect('chat:dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.title()}: {error}")
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('chat:dashboard')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            user.is_online = True
            user.save(update_fields=['is_online'])
            messages.success(request, f'Welcome back, {user.full_name}!')
            return redirect('chat:dashboard')
        else:
            messages.error(request, 'Invalid email or password.')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def logout_view(request):
    request.user.is_online = False
    request.user.update_last_seen()
    request.user.save(update_fields=['is_online'])
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('core:landing')

@login_required
def profile_view(request, user_id=None):
    if user_id:
        profile_user = get_object_or_404(User, id=user_id)
        is_own_profile = False
    else:
        profile_user = request.user
        is_own_profile = True
    
    # Check friendship status
    are_friends = False
    friend_request_sent = False
    friend_request_received = False
    
    if not is_own_profile:
        are_friends = Friendship.are_friends(request.user, profile_user)
        
        # Check for pending friend requests
        friend_request_sent = FriendRequest.objects.filter(
            from_user=request.user,
            to_user=profile_user,
            status='pending'
        ).exists()
        
        friend_request_received = FriendRequest.objects.filter(
            from_user=profile_user,
            to_user=request.user,
            status='pending'
        ).exists()
    
    context = {
        'profile_user': profile_user,
        'is_own_profile': is_own_profile,
        'are_friends': are_friends,
        'friend_request_sent': friend_request_sent,
        'friend_request_received': friend_request_received,
    }
    
    return render(request, 'accounts/profile.html', context)

@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    return render(request, 'accounts/edit_profile.html', {'form': form})

@login_required
def search_users(request):
    """API endpoint to search for users"""
    query = request.GET.get('q', '').strip()
    
    if not query:
        return JsonResponse({'users': []})
    
    if len(query) < 2:
        return JsonResponse({'users': [], 'message': 'Query too short'})
    
    try:
        users = User.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        ).exclude(id=request.user.id)[:10]
        
        users_data = []
        for user in users:
            # Check if already friends or request exists
            are_friends = Friendship.are_friends(request.user, user)
            request_sent = FriendRequest.objects.filter(
                from_user=request.user,
                to_user=user,
                status='pending'
            ).exists()
            
            users_data.append({
                'id': str(user.id),
                'name': user.full_name,
                'email': user.email,
                'avatar': user.avatar_url,
                'is_online': user.is_online,
                'are_friends': are_friends,
                'request_sent': request_sent
            })
        
        return JsonResponse({'users': users_data})
    
    except Exception as e:
        logger.error(f"Error searching users: {e}")
        return JsonResponse({'error': 'Search failed'}, status=500)

@login_required
@require_POST
def send_friend_request(request):
    """API endpoint to send friend request"""
    try:
        # Parse JSON data
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST
        
        user_id = data.get('user_id')
        
        if not user_id:
            return JsonResponse({'success': False, 'message': 'User ID is required'})
        
        # Get target user
        try:
            to_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'User not found'})
        
        # Check if trying to send request to self
        if to_user == request.user:
            return JsonResponse({'success': False, 'message': 'Cannot send friend request to yourself'})
        
        # Check if they're already friends
        if Friendship.are_friends(request.user, to_user):
            return JsonResponse({'success': False, 'message': 'You are already friends with this user'})
        
        # Check if request already exists (in either direction)
        existing_request = FriendRequest.objects.filter(
            Q(from_user=request.user, to_user=to_user) |
            Q(from_user=to_user, to_user=request.user),
            status='pending'
        ).first()
        
        if existing_request:
            if existing_request.from_user == request.user:
                return JsonResponse({'success': False, 'message': 'Friend request already sent'})
            else:
                return JsonResponse({'success': False, 'message': 'This user has already sent you a friend request'})
        
        # Create friend request
        friend_request = FriendRequest.objects.create(
            from_user=request.user,
            to_user=to_user
        )
        
        logger.info(f"Friend request created: {request.user.id} -> {to_user.id}")
        
        return JsonResponse({
            'success': True, 
            'message': f'Friend request sent to {to_user.full_name}!',
            'request_id': str(friend_request.id)
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.error(f"Error sending friend request: {e}")
        return JsonResponse({'success': False, 'message': 'An error occurred while sending friend request'}, status=500)

@login_required
@require_POST
def respond_friend_request(request):
    """API endpoint to accept or reject friend request"""
    try:
        # Parse JSON data
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST
        
        request_id = data.get('request_id')
        action = data.get('action')  # 'accept' or 'reject'
        
        if not request_id or not action:
            return JsonResponse({'success': False, 'message': 'Request ID and action are required'})
        
        if action not in ['accept', 'reject']:
            return JsonResponse({'success': False, 'message': 'Invalid action. Use "accept" or "reject"'})
        
        # Get friend request
        try:
            friend_request = FriendRequest.objects.get(
                id=request_id,
                to_user=request.user,
                status='pending'
            )
        except FriendRequest.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Friend request not found or already processed'})
        
        # Update request status
        friend_request.status = 'accepted' if action == 'accept' else 'rejected'
        friend_request.save()
        
        if action == 'accept':
            # Create friendship
            friendship = Friendship.objects.create(
                user1=friend_request.from_user,
                user2=friend_request.to_user
            )
            
            logger.info(f"Friendship created: {friend_request.from_user.id} <-> {friend_request.to_user.id}")
            
            return JsonResponse({
                'success': True, 
                'message': f'Friend request from {friend_request.from_user.full_name} accepted!',
                'friendship_id': str(friendship.id)
            })
        else:
            return JsonResponse({
                'success': True, 
                'message': f'Friend request from {friend_request.from_user.full_name} rejected.'
            })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.error(f"Error responding to friend request: {e}")
        return JsonResponse({'success': False, 'message': 'An error occurred while processing friend request'}, status=500)

@login_required
def friend_requests_view(request):
    # Received requests (pending)
    received_requests = FriendRequest.objects.filter(
        to_user=request.user,
        status='pending'
    ).select_related('from_user').order_by('-created_at')
    
    # Sent requests (pending)
    sent_requests = FriendRequest.objects.filter(
        from_user=request.user,
        status='pending'
    ).select_related('to_user').order_by('-created_at')
    
    context = {
        'received_requests': received_requests,
        'sent_requests': sent_requests,
    }
    
    return render(request, 'accounts/friend_requests.html', context)

@login_required
def friends_list_view(request):
    friends = Friendship.get_friends(request.user)
    
    # Add online status and other info
    for friend in friends:
        friend.is_friend_online = friend.is_online
    
    context = {
        'friends': friends,
    }
    
    return render(request, 'accounts/friends_list.html', context)

@login_required
@require_POST
def remove_friend(request):
    """API endpoint to remove a friend"""
    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST
        
        friend_id = data.get('friend_id')
        
        if not friend_id:
            return JsonResponse({'success': False, 'message': 'Friend ID is required'})
        
        try:
            friend = User.objects.get(id=friend_id)
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'User not found'})
        
        # Find and delete friendship
        friendship = Friendship.objects.filter(
            Q(user1=request.user, user2=friend) |
            Q(user1=friend, user2=request.user)
        ).first()
        
        if not friendship:
            return JsonResponse({'success': False, 'message': 'Friendship not found'})
        
        friendship.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Removed {friend.full_name} from your friends list'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.error(f"Error removing friend: {e}")
        return JsonResponse({'success': False, 'message': 'An error occurred while removing friend'}, status=500)

@login_required
def get_friend_status(request, user_id):
    """API endpoint to get friendship status with a user"""
    try:
        user = get_object_or_404(User, id=user_id)
        
        are_friends = Friendship.are_friends(request.user, user)
        
        friend_request_sent = FriendRequest.objects.filter(
            from_user=request.user,
            to_user=user,
            status='pending'
        ).exists()
        
        friend_request_received = FriendRequest.objects.filter(
            from_user=user,
            to_user=request.user,
            status='pending'
        ).exists()
        
        return JsonResponse({
            'are_friends': are_friends,
            'friend_request_sent': friend_request_sent,
            'friend_request_received': friend_request_received,
            'user_id': str(user.id),
            'user_name': user.full_name
        })
        
    except Exception as e:
        logger.error(f"Error getting friend status: {e}")
        return JsonResponse({'error': 'An error occurred'}, status=500)