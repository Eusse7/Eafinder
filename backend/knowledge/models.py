"""Modelos de la base de conocimiento de EAFinder.

Un `Document` es un documento institucional versionado (por ejemplo el
Reglamento Académico de pregrado). Un `Chunk` es un fragmento de ese
documento -- normalmente un artículo -- junto con su embedding, que es lo
que se recupera para responder una pregunta.

Restricción C03: no se usan bases de datos no relacionales. El embedding
se guarda como una lista de floats en un JSONField, y la similitud se
calcula en Python (ver services/retriever.py).
"""

import uuid

from django.db import models


class Document(models.Model):
    """Documento institucional indexado (US02, US12, US13, DB01-DB03)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(
        max_length=200,
        help_text="Ej: Reglamento Académico de los programas de pregrado",
    )
    version = models.CharField(
        max_length=50,
        default="1",
        help_text="Versión del documento. Ej: 2024-1",
    )
    source_url = models.URLField(
        blank=True,
        help_text="Enlace al documento oficial publicado por la Universidad.",
    )
    effective_date = models.DateField(
        null=True,
        blank=True,
        help_text="Fecha desde la cual rige esta versión.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text=(
            "Solo los documentos activos se usan para responder. "
            "Las versiones retiradas se conservan para trazabilidad."
        ),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    indexed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "documento"
        verbose_name_plural = "documentos"

    def __str__(self) -> str:
        estado = "activo" if self.is_active else "retirado"
        return f"{self.title} (v{self.version}, {estado})"

    @property
    def chunk_count(self) -> int:
        return self.chunks.count()


class Chunk(models.Model):
    """Fragmento recuperable de un documento (DB05)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="chunks",
    )
    position = models.PositiveIntegerField(
        help_text="Orden del fragmento dentro del documento.",
    )
    article_ref = models.CharField(
        max_length=120,
        blank=True,
        help_text="Ej: Artículo 42. Vacío si el fragmento no corresponde a un artículo.",
    )
    content = models.TextField()
    embedding = models.JSONField(
        default=list,
        blank=True,
        help_text="Vector de embedding. Lista de floats.",
    )

    class Meta:
        ordering = ["document", "position"]
        verbose_name = "fragmento"
        verbose_name_plural = "fragmentos"

    def __str__(self) -> str:
        return self.article_ref or f"Fragmento {self.position}"

    @property
    def citation(self) -> str:
        """Cita legible para mostrar al usuario (US09)."""
        if self.article_ref:
            return f"{self.document.title}, {self.article_ref}"
        return self.document.title
