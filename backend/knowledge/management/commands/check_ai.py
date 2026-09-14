"""Diagnostica la conexión con el proveedor de IA.

Prueba por separado las dos cosas que EAFinder necesita —calcular
embeddings y generar texto— y muestra el error completo del proveedor si
alguna falla. Útil cuando el chat responde "No pude comunicarme con el
servicio de inteligencia artificial" y no se sabe por qué.

    python manage.py check_ai
"""

from __future__ import annotations

from django.conf import settings
from django.core.management.base import BaseCommand

from knowledge.models import Chunk, Document
from knowledge.services.ai_provider import (
    AIProviderError,
    embed_query,
    generate_answer,
)


def enmascarar(clave: str) -> str:
    if not clave:
        return "(vacía)"
    if len(clave) <= 8:
        return "***"
    return f"{clave[:4]}...{clave[-4:]}"


class Command(BaseCommand):
    help = "Verifica que la clave y los modelos del proveedor de IA funcionen."

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("Configuración"))
        self.stdout.write(f"  Proveedor:          {settings.AI_PROVIDER}")
        self.stdout.write(f"  Modelo de chat:     {settings.AI_CHAT_MODEL}")
        self.stdout.write(f"  Modelo de embedding:{settings.AI_EMBEDDING_MODEL}")
        self.stdout.write(f"  Clave:              {enmascarar(settings.AI_API_KEY)}")

        self.stdout.write(self.style.MIGRATE_HEADING("\nBase de conocimiento"))
        documentos = Document.objects.filter(is_active=True).count()
        fragmentos = Chunk.objects.filter(document__is_active=True).exclude(
            embedding=[]
        ).count()
        self.stdout.write(f"  Documentos activos: {documentos}")
        self.stdout.write(f"  Fragmentos con embedding: {fragmentos}")

        if fragmentos == 0:
            self.stdout.write(
                self.style.WARNING(
                    "  Sin fragmentos indexados, el chat no puede responder. "
                    "Corre manage.py ingest_document."
                )
            )

        fallos = 0

        self.stdout.write(self.style.MIGRATE_HEADING("\n1. Embeddings"))
        try:
            vector = embed_query("¿Cuándo puedo cancelar una asignatura?")
        except AIProviderError as error:
            fallos += 1
            self.stdout.write(self.style.ERROR(f"  FALLA\n{error}"))
        else:
            self.stdout.write(
                self.style.SUCCESS(f"  OK — vector de {len(vector)} dimensiones")
            )

        self.stdout.write(self.style.MIGRATE_HEADING("\n2. Generación de texto"))
        try:
            respuesta = generate_answer(
                "Responde en español, en una sola frase corta.",
                "Di exactamente: la conexion funciona.",
            )
        except AIProviderError as error:
            fallos += 1
            self.stdout.write(self.style.ERROR(f"  FALLA\n{error}"))
        else:
            self.stdout.write(self.style.SUCCESS(f'  OK — respondió: "{respuesta}"'))

        self.stdout.write("")

        if fallos:
            self.stdout.write(
                self.style.ERROR(
                    f"{fallos} de 2 pruebas fallaron. El detalle del proveedor "
                    "está arriba."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS("Todo en orden. El chat debería responder bien.")
            )
