from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('conversation/<uuid:conversation_id>/', views.conversation_view, name='conversation'),
    path('start/<uuid:user_id>/', views.start_conversation_view, name='start_conversation'),
    
    # API endpoints
    path('api/send-message/', views.send_message_api, name='send_message_api'),
    path('api/messages/<uuid:conversation_id>/', views.get_messages_api, name='get_messages_api'),
    path('api/online-users/', views.get_online_users_api, name='get_online_users_api'),
    path('api/update-status/', views.update_user_status, name='update_user_status'),
    # Add these to your existing urlpatterns list
    path('api/friend-request/accept/', views.accept_friend_request_api, name='accept_friend_request_api'),
    path('api/friend-request/decline/', views.decline_friend_request_api, name='decline_friend_request_api'),
    ]