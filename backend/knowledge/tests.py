"""Pruebas de la base de conocimiento y del pipeline RAG.

No se llama al proveedor externo: los embeddings y la generación se
sustituyen por dobles de prueba, de modo que los tests corren sin API key
y sin costo.
"""

from unittest.mock import patch

from django.test import TestCase, override_settings

from knowledge.models import Chunk, Document
from knowledge.services import chunker, rag
from knowledge.services.retriever import cosine_similarity

REGLAMENTO = """
REGLAMENTO ACADÉMICO

Artículo 12. Matrícula. El estudiante debe realizar su matrícula dentro de
las fechas fijadas. La matrícula comprende la inscripción de asignaturas y
el pago de los derechos correspondientes.

Artículo 13. Cancelación de asignaturas. El estudiante podrá cancelar
asignaturas hasta la semana octava del semestre sin que la nota aparezca en
su historia académica.

Artículo 14. Prueba académica. El estudiante queda en prueba académica
cuando su promedio semestral sea inferior a tres punto cero (3.0).
"""


class ChunkerTests(TestCase):
    def test_divide_por_articulo(self):
        chunks = chunker.split(REGLAMENTO)

        self.assertEqual(len(chunks), 3)
        self.assertEqual(chunks[0].article_ref, "Artículo 12")
        self.assertEqual(chunks[2].article_ref, "Artículo 14")
        self.assertIn("prueba académica", chunks[2].content.lower())

    def test_texto_sin_articulos_se_divide_por_tamano(self):
        chunks = chunker.split("Un texto plano sin artículos numerados.")

        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0].article_ref, "")


class CosineSimilarityTests(TestCase):
    def test_vectores_iguales(self):
        self.assertAlmostEqual(cosine_similarity([1.0, 0.0], [1.0, 0.0]), 1.0)

    def test_vectores_ortogonales(self):
        self.assertAlmostEqual(cosine_similarity([1.0, 0.0], [0.0, 1.0]), 0.0)

    def test_vector_vacio_no_revienta(self):
        self.assertEqual(cosine_similarity([], [1.0]), 0.0)


class RagTests(TestCase):
    def setUp(self):
        self.document = Document.objects.create(
            title="Reglamento Académico de los programas de pregrado",
            version="2025-1",
        )
        Chunk.objects.create(
            document=self.document,
            position=0,
            article_ref="Artículo 13",
            content="El estudiante podrá cancelar asignaturas hasta la semana octava.",
            embedding=[1.0, 0.0, 0.0],
        )
        Chunk.objects.create(
            document=self.document,
            position=1,
            article_ref="Artículo 14",
            content="El estudiante queda en prueba académica con promedio inferior a 3.0.",
            embedding=[0.0, 1.0, 0.0],
        )

    def test_responde_citando_el_articulo_relevante(self):
        with (
            patch(
                "knowledge.services.retriever.embed_query",
                return_value=[1.0, 0.0, 0.0],
            ),
            patch(
                "knowledge.services.rag.generate_answer",
                return_value="Puedes cancelar hasta la semana octava (Artículo 13).",
            ),
        ):
            answer = rag.answer_question("¿hasta cuando puedo cancelar materias?")

        self.assertTrue(answer.grounded)
        self.assertIn("Artículo 13", answer.content)
        self.assertEqual(answer.sources[0].chunk.article_ref, "Artículo 13")

    @override_settings(RAG_MIN_RELEVANCE=0.9)
    def test_sin_contexto_relevante_declara_su_limitacion(self):
        """US10: si nada supera el umbral, no se inventa la respuesta."""
        with (
            patch(
                "knowledge.services.retriever.embed_query",
                return_value=[0.0, 0.0, 1.0],
            ),
            patch("knowledge.services.rag.generate_answer") as generate,
        ):
            answer = rag.answer_question("¿cuánto cuesta el parqueadero?")

        generate.assert_not_called()
        self.assertFalse(answer.grounded)
        self.assertIn("no encontré información suficiente", answer.content.lower())

    def test_base_de_conocimiento_vacia(self):
        Chunk.objects.all().delete()

        answer = rag.answer_question("¿cómo me matriculo?")

        self.assertFalse(answer.grounded)
        self.assertIn("no tengo documentos indexados", answer.content.lower())

    def test_documento_retirado_no_se_usa(self):
        """SRS 1.4-e: las versiones retiradas se conservan pero no responden."""
        self.document.is_active = False
        self.document.save()

        answer = rag.answer_question("¿hasta cuando puedo cancelar materias?")

        self.assertFalse(answer.grounded)


class IngestCommandTests(TestCase):
    """El parser del comando se construye sin chocar con las opciones de Django.

    Django ya define --version, --verbosity, --settings, --pythonpath,
    --traceback, --no-color, --force-color y --skip-checks en todos los
    comandos. Si uno propio repite alguna, `manage.py` revienta antes de
    ejecutar nada. Por eso la versión del documento se pasa con
    --doc-version.
    """

    def test_el_parser_se_construye(self):
        from knowledge.management.commands.ingest_document import Command

        parser = Command().create_parser("manage.py", "ingest_document")
        opciones = parser.parse_args(
            ["reglamento.pdf", "--title", "Reglamento", "--doc-version", "2025-1"]
        )

        self.assertEqual(opciones.path, "reglamento.pdf")
        self.assertEqual(opciones.title, "Reglamento")
        self.assertEqual(opciones.doc_version, "2025-1")
        self.assertFalse(opciones.retire_previous)


class ReintentosTests(TestCase):
    """El adaptador aguanta los 429 del tier gratuito en vez de abortar."""

    def _respuesta(self, status_code, payload=None):
        import httpx

        return httpx.Response(
            status_code=status_code,
            json=payload if payload is not None else {"ok": True},
            request=httpx.Request("POST", "https://example.test"),
        )

    def test_reintenta_tras_un_429_y_termina_bien(self):
        from knowledge.services import ai_provider

        respuestas = [self._respuesta(429, {"error": "rate"}), self._respuesta(200)]

        with (
            patch("httpx.post", side_effect=respuestas) as post,
            patch("knowledge.services.ai_provider.time.sleep") as dormir,
        ):
            resultado = ai_provider._post("https://example.test", json={})

        self.assertEqual(resultado, {"ok": True})
        self.assertEqual(post.call_count, 2)
        dormir.assert_called_once()

    def test_un_400_no_se_reintenta(self):
        from knowledge.services.ai_provider import AIProviderError, _post

        with (
            patch("httpx.post", return_value=self._respuesta(400, {"error": "malo"})) as post,
            patch("knowledge.services.ai_provider.time.sleep"),
            self.assertRaises(AIProviderError),
        ):
            _post("https://example.test", json={})

        self.assertEqual(post.call_count, 1)

    def test_se_rinde_tras_agotar_los_reintentos(self):
        from knowledge.services import ai_provider

        with (
            patch("httpx.post", return_value=self._respuesta(429, {"error": "rate"})) as post,
            patch("knowledge.services.ai_provider.time.sleep"),
            self.assertRaises(ai_provider.AIProviderError) as capturado,
        ):
            ai_provider._post("https://example.test", json={})

        self.assertEqual(post.call_count, ai_provider.MAX_REINTENTOS)
        self.assertIn("límite de peticiones", str(capturado.exception))

    def test_respeta_la_cabecera_retry_after(self):
        from knowledge.services.ai_provider import _espera

        import httpx

        response = httpx.Response(
            status_code=429,
            headers={"Retry-After": "30"},
            request=httpx.Request("POST", "https://example.test"),
        )

        self.assertEqual(_espera(response, 0), 30.0)


class RespuestaGeminiTests(TestCase):
    """Lectura de la respuesta de Gemini, incluidos los casos vacíos."""

    def test_extrae_el_texto(self):
        from knowledge.services.ai_provider import _texto_de_respuesta

        data = {"candidates": [{"content": {"parts": [{"text": "  Hola  "}]}}]}

        self.assertEqual(_texto_de_respuesta(data), "Hola")

    def test_une_varias_partes(self):
        from knowledge.services.ai_provider import _texto_de_respuesta

        data = {
            "candidates": [
                {"content": {"parts": [{"text": "Uno "}, {"text": "dos"}]}}
            ]
        }

        self.assertEqual(_texto_de_respuesta(data), "Uno dos")

    def test_max_tokens_explica_el_presupuesto_de_razonamiento(self):
        """Gemini 3.x descuenta su razonamiento de maxOutputTokens."""
        from knowledge.services.ai_provider import AIProviderError, _texto_de_respuesta

        data = {"candidates": [{"content": {"parts": []}, "finishReason": "MAX_TOKENS"}]}

        with self.assertRaises(AIProviderError) as capturado:
            _texto_de_respuesta(data)

        self.assertIn("AI_MAX_OUTPUT_TOKENS", str(capturado.exception))

    def test_sin_candidatos(self):
        from knowledge.services.ai_provider import AIProviderError, _texto_de_respuesta

        with self.assertRaises(AIProviderError):
            _texto_de_respuesta({"candidates": []})

    def test_thinking_level_solo_en_gemini_3(self):
        from knowledge.services.ai_provider import _config_de_generacion

        self.assertIn("thinkingLevel", _config_de_generacion("gemini-3.6-flash"))
        self.assertNotIn("thinkingLevel", _config_de_generacion("gemini-2.5-flash"))

    @override_settings(AI_THINKING_LEVEL="")
    def test_thinking_level_vacio_no_se_envia(self):
        from knowledge.services.ai_provider import _config_de_generacion

        self.assertNotIn("thinkingLevel", _config_de_generacion("gemini-3.6-flash"))
