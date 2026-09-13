from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Chat, Message


@api_view(["POST"])
def create_chat(request):
    session_id = request.data.get("session_id")

    if not session_id:
        return Response(
            {"error": "El session_id es obligatorio."},
            status=400,
        )

    active_chats = Chat.objects.filter(session_id=session_id).count()

    if active_chats >= 5:
        return Response(
            {"error": "Has alcanzado el límite de 5 chats."},
            status=400,
        )

    chat = Chat.objects.create(
        session_id=session_id,
    )

    return Response(
        {
            "id": str(chat.id),
            "title": chat.title,
        }
    )


@api_view(["GET"])
def get_chats(request):
    session_id = request.query_params.get("session_id")

    if not session_id:
        return Response(
            {"error": "El session_id es obligatorio."},
            status=400,
        )

    chats = Chat.objects.filter(
        session_id=session_id,
    ).order_by("-created_at")

    return Response(
        [
            {
                "id": str(chat.id),
                "title": chat.title,
                "created_at": chat.created_at,
            }
            for chat in chats
        ]
    )


@api_view(["POST"])
def create_message(request, chat_id):
    content = request.data.get("content")

    if not content:
        return Response(
            {"error": "El contenido es obligatorio."},
            status=400,
        )

    chat = get_object_or_404(Chat, id=chat_id)

    user_message = Message.objects.create(
        chat=chat,
        role=Message.Role.USER,
        content=content,
    )

    Message.objects.create(
        chat=chat,
        role=Message.Role.ASSISTANT,
        content="NA",
    )

    return Response(
        {
            "id": str(user_message.id),
            "chat_id": str(chat.id),
            "content": user_message.content,
            "role": user_message.role,
        }
    )


@api_view(["GET", "DELETE"])
def get_chat(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)

    if request.method == "DELETE":
        chat.delete()

        return Response(status=204)

    limit = 10
    before = request.query_params.get("before")

    messages_query = Message.objects.filter(chat=chat)

    if before:
        cursor_message = get_object_or_404(
            Message,
            id=before,
            chat=chat,
        )

        messages_query = messages_query.filter(
            Q(created_at__lt=cursor_message.created_at)
            | Q(
                created_at=cursor_message.created_at,
                id__lt=cursor_message.id,
            )
        )

    messages = list(messages_query.order_by("-created_at", "-id")[: limit + 1])

    has_more = len(messages) > limit

    messages = messages[:limit]
    messages.reverse()

    next_cursor = str(messages[0].id) if has_more and messages else None

    return Response(
        {
            "id": str(chat.id),
            "title": chat.title,
            "created_at": chat.created_at,
            "messages": [
                {
                    "id": str(message.id),
                    "role": message.role,
                    "content": message.content,
                    "created_at": message.created_at,
                }
                for message in messages
            ],
            "has_more": has_more,
            "next_cursor": next_cursor,
        }
    )


@api_view(["GET"])
def chat_exists(request, chat_id):
    exists = Chat.objects.filter(id=chat_id).exists()

    return Response(
        {
            "exists": exists,
        }
    )
