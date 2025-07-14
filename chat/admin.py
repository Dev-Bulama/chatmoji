from django.contrib import admin
from .models import Conversation, Message, MessageRead

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'conversation_type', 'created_by', 'created_at', 'updated_at', 'participant_count')
    list_filter = ('conversation_type', 'created_at')
    search_fields = ('name', 'created_by__email', 'participants__email')
    ordering = ('-updated_at',)
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('participants',)
    
    def participant_count(self, obj):
        return obj.participants.count()
    participant_count.short_description = 'Participants'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by').prefetch_related('participants')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'conversation', 'content_preview', 'message_type', 'timestamp', 'is_deleted')
    list_filter = ('message_type', 'timestamp', 'is_deleted')
    search_fields = ('sender__email', 'content', 'conversation__name')
    ordering = ('-timestamp',)
    readonly_fields = ('timestamp', 'emoji_content')
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('sender', 'conversation')

@admin.register(MessageRead)
class MessageReadAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'read_at')
    list_filter = ('read_at',)
    search_fields = ('user__email', 'message__content')
    ordering = ('-read_at',)
    readonly_fields = ('read_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'message')