from django.urls import path

from .views import chat_exists, create_chat, create_message, get_chat, get_chats

urlpatterns = [
    path("", create_chat),
    path("list/", get_chats),
    path("<uuid:chat_id>/messages/", create_message),
    path("<uuid:chat_id>/exists/", chat_exists),
    path("<uuid:chat_id>/", get_chat),
]
