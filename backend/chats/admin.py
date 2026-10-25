from django.contrib import admin
from django.template.response import TemplateResponse
from django.urls import path

from .models import Chat, Message, MessageSource
from .views import get_analytics_data


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
    change_list_template = "admin/chats/chat_change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "analytics/",
                self.admin_site.admin_view(self.analytics_view),
                name="chats_analytics",
            ),
        ]
        return custom_urls + urls

    def analytics_view(self, request):
        data = get_analytics_data()
        context = {
            **self.admin_site.each_context(request),
            "title": "Panel de Analítica de Búsquedas (US05)",
            "analytics": data,
        }
        return TemplateResponse(request, "admin/chats_analytics.html", context)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("role", "content", "chat", "feedback", "moderated", "created_at")
    list_filter = ("role", "feedback", "moderated")
    inlines = [MessageSourceInline]
