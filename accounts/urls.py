from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/<uuid:user_id>/', views.profile_view, name='user_profile'),
    path('edit-profile/', views.edit_profile_view, name='edit_profile'),
    path('friend-requests/', views.friend_requests_view, name='friend_requests'),
    path('friends/', views.friends_list_view, name='friends_list'),
    
    # AJAX endpoints
    path('api/search-users/', views.search_users, name='search_users'),
    path('api/send-friend-request/', views.send_friend_request, name='send_friend_request'),
    path('api/respond-friend-request/', views.respond_friend_request, name='respond_friend_request'),
    path('api/remove-friend/', views.remove_friend, name='remove_friend'),
    path('api/friend-status/<uuid:user_id>/', views.get_friend_status, name='get_friend_status'),
]