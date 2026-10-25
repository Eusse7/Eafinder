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

    # US15: valoración de respuestas ---------------------------------------

    def _mensaje_del_asistente(self, chat_id):
        with patch(
            "chats.views.answer_question",
            return_value=Answer(content="Respuesta de prueba.", grounded=True),
        ):
            response = self.client.post(
                f"/api/chats/{chat_id}/messages/",
                {"content": "¿Cómo cancelo una materia?"},
                content_type="application/json",
            )
        return response.json()["assistant_message"]["id"]

    def test_feedback_up_se_guarda(self):
        chat_id = self.crear_chat()
        message_id = self._mensaje_del_asistente(chat_id)

        response = self.client.patch(
            f"/api/chats/{chat_id}/messages/{message_id}/feedback/",
            {"feedback": "up"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["feedback"], "up")
        self.assertEqual(Message.objects.get(id=message_id).feedback, "up")

    def test_feedback_vacio_quita_la_valoracion(self):
        chat_id = self.crear_chat()
        message_id = self._mensaje_del_asistente(chat_id)

        self.client.patch(
            f"/api/chats/{chat_id}/messages/{message_id}/feedback/",
            {"feedback": "down"},
            content_type="application/json",
        )
        response = self.client.patch(
            f"/api/chats/{chat_id}/messages/{message_id}/feedback/",
            {"feedback": ""},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Message.objects.get(id=message_id).feedback, "")

    def test_feedback_invalido_es_rechazado(self):
        chat_id = self.crear_chat()
        message_id = self._mensaje_del_asistente(chat_id)

        response = self.client.patch(
            f"/api/chats/{chat_id}/messages/{message_id}/feedback/",
            {"feedback": "amazing"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)

    def test_no_se_puede_valorar_un_mensaje_del_usuario(self):
        chat_id = self.crear_chat()
        chat = Chat.objects.get(id=chat_id)
        user_message = Message.objects.create(
            chat=chat, role=Message.Role.USER, content="hola"
        )

        response = self.client.patch(
            f"/api/chats/{chat_id}/messages/{user_message.id}/feedback/",
            {"feedback": "up"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)

    # US20: filtro de moderación en el pipeline ----------------------------

    def test_pregunta_sensible_no_llama_al_pipeline(self):
        """Una pregunta sensible se corta en moderación, antes del RAG.

        No se mockea answer_question: corre el pipeline real. El filtro de
        moderación responde antes de retrieve(), así que no se llama al
        proveedor de IA ni se necesita clave.
        """
        chat_id = self.crear_chat()

        response = self.client.post(
            f"/api/chats/{chat_id}/messages/",
            {"content": "quiero suicidarme"},
            content_type="application/json",
        )

        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(body["assistant_message"]["moderated"])
        self.assertIn("106", body["assistant_message"]["content"])

    def test_pregunta_normal_no_se_marca_como_moderada(self):
        chat_id = self.crear_chat()

        with patch(
            "chats.views.answer_question",
            return_value=Answer(content="Respuesta normal.", grounded=True),
        ):
            response = self.client.post(
                f"/api/chats/{chat_id}/messages/",
                {"content": "¿Cómo me matriculo?"},
                content_type="application/json",
            )

        self.assertFalse(response.json()["assistant_message"]["moderated"])

    # US05: panel de analítica de búsquedas --------------------------------

    def test_analytics_sin_consultas_muestra_estado_vacio(self):
        """Escenario 2 de US05: sin datos registrados no se muestran métricas ficticias."""
        response = self.client.get("/api/chats/analytics/")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data["has_data"])
        self.assertEqual(data["total_queries"], 0)
        self.assertIsNone(data["satisfaction_rate"])
        self.assertEqual(data["frequent_topics"], [])
        self.assertEqual(data["daily_volume"], [])

    def test_analytics_con_consultas_calcula_metricas_y_temas_frecuentes(self):
        """Escenario 1 de US05: métricas de volumen, temas frecuentes y satisfacción."""
        chat_id = self.crear_chat()
        chat = Chat.objects.get(id=chat_id)

        # Crear preguntas de distintos temas
        m1 = Message.objects.create(
            chat=chat,
            role=Message.Role.USER,
            content="¿Hasta cuándo puedo realizar la matrícula?",
        )
        a1 = Message.objects.create(
            chat=chat,
            role=Message.Role.ASSISTANT,
            content="La matrícula se realiza según las fechas oficiales.",
            feedback="up",
        )
        m2 = Message.objects.create(
            chat=chat,
            role=Message.Role.USER,
            content="¿Cómo cancelo una asignatura?",
        )
        a2 = Message.objects.create(
            chat=chat,
            role=Message.Role.ASSISTANT,
            content="Puedes cancelar hasta la semana octava.",
            feedback="down",
        )
        m3 = Message.objects.create(
            chat=chat,
            role=Message.Role.USER,
            content="¿En qué consiste la prueba académica y qué promedio exige?",
        )

        response = self.client.get("/api/chats/analytics/")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["has_data"])
        self.assertEqual(data["total_queries"], 3)
        self.assertEqual(data["total_chats"], 1)
        self.assertEqual(data["feedback_up"], 1)
        self.assertEqual(data["feedback_down"], 1)
        self.assertEqual(data["satisfaction_rate"], 50.0)

        # Verificar que se detectaron los temas frecuentes
        temas_encontrados = {item["topic"]: item["count"] for item in data["frequent_topics"]}
        self.assertIn("Matrícula e inscripción", temas_encontrados)
        self.assertIn("Cancelación de asignaturas", temas_encontrados)
        self.assertIn("Prueba académica y promedio", temas_encontrados)

        # Volumen diario
        self.assertTrue(len(data["daily_volume"]) >= 1)
        self.assertEqual(data["daily_volume"][0]["count"], 3)

    def test_admin_analytics_view_renderiza_panel(self):
        from django.contrib.auth.models import User

        User.objects.create_superuser(
            username="admin", password="password", email="admin@test.com"
        )
        self.client.login(username="admin", password="password")

        response = self.client.get("/admin/chats/chat/analytics/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Panel de Analítica de Búsquedas")
