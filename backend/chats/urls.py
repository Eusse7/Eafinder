from django.urls import path

from .views import (
    analytics,
    chat_exists,
    create_chat,
    create_message,
    get_chat,
    get_chats,
    health,
    knowledge_gaps_report,
    set_feedback,
)

urlpatterns = [
    path("", create_chat),
    path("health/", health),
    path("analytics/", analytics),
    path("knowledge-gaps/", knowledge_gaps_report),
    path("list/", get_chats),
    path("<uuid:chat_id>/messages/", create_message),
    path("<uuid:chat_id>/messages/<uuid:message_id>/feedback/", set_feedback),
    path("<uuid:chat_id>/exists/", chat_exists),
    path("<uuid:chat_id>/", get_chat),
]
