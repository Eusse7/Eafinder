"""Carga e indexa un documento institucional (US02, US12).

Ejemplos:

    uv run python manage.py ingest_document docs/reglamento.pdf \
        --title "Reglamento Académico de los programas de pregrado" \
        --doc-version 2024-1

    uv run python manage.py ingest_document docs/reglamento_2025.pdf \
        --title "Reglamento Académico de los programas de pregrado" \
        --doc-version 2025-1 --retire-previous
"""

from __future__ import annotations

from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from knowledge.models import Document
from knowledge.services import indexer
from knowledge.services.ai_provider import AIProviderError


class Command(BaseCommand):
    help = "Carga un documento (.pdf, .docx, .txt, .md) y lo indexa en la base de conocimiento."

    def add_arguments(self, parser):
        parser.add_argument("path", type=str, help="Ruta al archivo del documento.")
        parser.add_argument(
            "--title",
            required=True,
            help="Título del documento tal como se va a citar.",
        )
        # Ojo: no se puede llamar --version, porque Django ya usa esa opción
        # para mostrar su propia versión.
        parser.add_argument(
            "--doc-version",
            default="1",
            help="Versión del documento. Ej: 2025-1",
        )
        parser.add_argument("--source-url", default="", help="Enlace al documento oficial.")
        parser.add_argument(
            "--retire-previous",
            action="store_true",
            help=(
                "Marca como retiradas las versiones anteriores con el mismo título. "
                "Se conservan para trazabilidad, pero dejan de usarse al responder."
            ),
        )

    def handle(self, *args, **options):
        path = Path(options["path"])

        if not path.exists():
            raise CommandError(f"No existe el archivo: {path}")

        title = options["title"]

        try:
            with transaction.atomic():
                if options["retire_previous"]:
                    retirados = Document.objects.filter(
                        title=title, is_active=True
                    ).update(is_active=False)
                    if retirados:
                        self.stdout.write(
                            self.style.WARNING(f"Versiones retiradas: {retirados}")
                        )

                document = Document.objects.create(
                    title=title,
                    version=options["doc_version"],
                    source_url=options["source_url"],
                    is_active=True,
                )

                self.stdout.write(f"Extrayendo texto de {path.name}...")

                def progreso(hechos: int, total: int) -> None:
                    self.stdout.write(
                        f"  Embeddings: {hechos}/{total} fragmentos", ending="\r"
                    )
                    self.stdout.flush()

                total = indexer.index_from_file(document, path, progreso)
                self.stdout.write("")

        except AIProviderError as error:
            raise CommandError(str(error)) from error
        except (ValueError, ImportError) as error:
            raise CommandError(str(error)) from error

        self.stdout.write(
            self.style.SUCCESS(
                f"Listo. '{title}' v{options['doc_version']} indexado "
                f"con {total} fragmentos. Ya es consultable desde el chat."
            )
        )
