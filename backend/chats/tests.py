"""Pruebas de la API de chat."""

from unittest.mock import patch
from uuid import uuid4

from django.test import TestCase

from knowledge.services.rag import Answer

from .models import Chat, Message
from .views import build_title


class TitleTests(TestCase):
    def test_titulo_corto_se_conserva(self):
        self.assertEqual(build_title("¿Cómo me matriculo?"), "¿Cómo me matriculo?")

    def test_titulo_largo_se_recorta(self):
        titulo = build_title("a" * 120)
        self.assertLessEqual(len(titulo), 60)
        self.assertTrue(titulo.endswith("…"))


class ChatApiTests(TestCase):
    def setUp(self):
        self.session_id = str(uuid4())

    def crear_chat(self):
        response = self.client.post(
            "/api/chats/",
            {"session_id": self.session_id},
            content_type="application/json",
        )
        return response.json()["id"]

    def test_limite_de_cinco_chats_por_sesion(self):
        for _ in range(5):
            self.crear_chat()

        response = self.client.post(
            "/api/chats/",
            {"session_id": self.session_id},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)

    def test_enviar_mensaje_devuelve_respuesta_y_titula_el_chat(self):
        chat_id = self.crear_chat()

        with patch(
            "chats.views.answer_question",
            return_value=Answer(content="Respuesta de prueba.", grounded=True),
        ):
            response = self.client.post(
                f"/api/chats/{chat_id}/messages/",
                {"content": "¿Cómo cancelo una materia?"},
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["assistant_message"]["content"], "Respuesta de prueba.")
        self.assertEqual(body["chat_title"], "¿Cómo cancelo una materia?")
        self.assertEqual(Message.objects.filter(chat_id=chat_id).count(), 2)

    def test_mensaje_vacio_es_rechazado(self):
        chat_id = self.crear_chat()

        response = self.client.post(
            f"/api/chats/{chat_id}/messages/",
            {"content": "   "},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)

    def test_health(self):
        response = self.client.get("/api/chats/health/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_borrar_chat(self):
        chat_id = self.crear_chat()

        response = self.client.delete(f"/api/chats/{chat_id}/")

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Chat.objects.filter(id=chat_id).exists())
