from django.contrib import admin

from .models import Chat, Message, MessageSource


class MessageSourceInline(admin.TabularInline):
    model = MessageSource
    extra = 0
    readonly_fields = ("document_title", "article_ref", "excerpt", "relevance")
    can_delete = False
    max_num = 0


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ("title", "session_id", "created_at")
    search_fields = ("title",)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("role", "content", "chat", "created_at")
    list_filter = ("role",)
    inlines = [MessageSourceInline]
