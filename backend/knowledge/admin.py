from django.contrib import admin, messages
from django.utils import timezone

from .models import Chunk, Document, KnowledgeGap
from .services import indexer
from .services.ai_provider import AIProviderError


class ChunkInline(admin.TabularInline):
    model = Chunk
    extra = 0
    fields = ("position", "article_ref", "content")
    readonly_fields = ("position", "article_ref", "content")
    can_delete = False
    max_num = 0


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "version", "is_active", "chunk_count", "indexed_at")
    list_filter = ("is_active",)
    search_fields = ("title",)
    readonly_fields = ("created_at", "indexed_at")
    inlines = [ChunkInline]
    actions = ["reindex_documents", "retire_documents", "activate_documents"]
    change_list_template = "admin/knowledge/document_change_list.html"

    def get_urls(self):
        from django.urls import path

        urls = super().get_urls()
        custom_urls = [
            path(
                "upload/",
                self.admin_site.admin_view(self.upload_document_view),
                name="knowledge_document_upload",
            ),
        ]
        return custom_urls + urls

    def upload_document_view(self, request):
        """Carga y procesa un nuevo documento desde la interfaz web (US12)."""
        import tempfile
        from pathlib import Path
        from django.db import transaction
        from django.shortcuts import redirect
        from django.template.response import TemplateResponse

        context = {
            **self.admin_site.each_context(request),
            "title": "Cargar e indexar reglamento (US12)",
        }

        if request.method == "POST":
            uploaded_file = request.FILES.get("file")
            title = request.POST.get("title", "").strip()
            version = request.POST.get("version", "1").strip()
            source_url = request.POST.get("source_url", "").strip()
            retire_previous = bool(request.POST.get("retire_previous"))

            context.update({
                "title": title,
                "version": version,
                "source_url": source_url,
            })

            if not uploaded_file:
                messages.error(request, "Debes seleccionar un archivo para cargar.")
                return TemplateResponse(request, "admin/knowledge/document_upload.html", context)

            if not title:
                messages.error(request, "El título del documento es obligatorio.")
                return TemplateResponse(request, "admin/knowledge/document_upload.html", context)

            suffix = Path(uploaded_file.name).suffix.lower()
            allowed_suffixes = {".pdf", ".docx", ".txt", ".md"}

            # Escenario 2 de US12: archivo no válido
            if suffix not in allowed_suffixes:
                messages.error(
                    request,
                    f"Formato no permitido: '{suffix}'. Solo se admiten archivos .pdf, .docx, .txt o .md.",
                )
                return TemplateResponse(request, "admin/knowledge/document_upload.html", context)

            # Escenario 1 de US12: procesar e incorporar el documento
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
                    for chunk in uploaded_file.chunks():
                        temp.write(chunk)
                    temp_path = Path(temp.name)

                try:
                    with transaction.atomic():
                        if retire_previous:
                            Document.objects.filter(title=title, is_active=True).update(is_active=False)

                        document = Document.objects.create(
                            title=title,
                            version=version,
                            source_url=source_url,
                            is_active=True,
                        )

                        total = indexer.index_from_file(document, temp_path)

                    messages.success(
                        request,
                        f"¡Documento incorporado exitosamente! '{title}' (v{version}) fue indexado con {total} fragmentos.",
                    )
                    return redirect("admin:knowledge_document_changelist")

                finally:
                    if temp_path.exists():
                        temp_path.unlink()

            except (AIProviderError, ValueError, ImportError) as error:
                messages.error(request, f"Error al procesar el archivo: {error}")
                return TemplateResponse(request, "admin/knowledge/document_upload.html", context)

        return TemplateResponse(request, "admin/knowledge/document_upload.html", context)


    @admin.action(description="Re-indexar (recalcular embeddings)")
    def reindex_documents(self, request, queryset):
        for document in queryset:
            try:
                total = indexer.reindex(document)
            except (AIProviderError, ValueError) as error:
                self.message_user(
                    request, f"{document}: {error}", level=messages.ERROR
                )
            else:
                self.message_user(
                    request,
                    f"{document}: {total} fragmentos re-indexados correctamente.",
                    level=messages.SUCCESS,
                )

    @admin.action(description="Retirar (dejar de usar al responder)")
    def retire_documents(self, request, queryset):
        total = queryset.update(is_active=False)
        self.message_user(request, f"{total} documento(s) retirado(s).")

    @admin.action(description="Activar")
    def activate_documents(self, request, queryset):
        total = queryset.update(is_active=True)
        self.message_user(request, f"{total} documento(s) activado(s).")


@admin.register(Chunk)
class ChunkAdmin(admin.ModelAdmin):
    list_display = ("article_ref", "document", "position")
    list_filter = ("document",)
    search_fields = ("article_ref", "content")


@admin.register(KnowledgeGap)
class KnowledgeGapAdmin(admin.ModelAdmin):
    """Panel de revisión de consultas sin respuesta y brechas de conocimiento (US18)."""

    list_display = ("query", "reason", "max_similarity", "status", "created_at")
    list_filter = ("status", "reason", "created_at")
    search_fields = ("query", "normalized_query", "notes")
    readonly_fields = ("created_at", "normalized_query")
    actions = ["mark_as_reviewed", "mark_as_resolved", "mark_as_dismissed"]

    @admin.action(description="Marcar como revisada")
    def mark_as_reviewed(self, request, queryset):
        total = queryset.update(status=KnowledgeGap.Status.REVIEWED, reviewed_at=timezone.now())
        self.message_user(request, f"{total} brecha(s) marcada(s) como revisada(s).")

    @admin.action(description="Marcar como resuelta (documento incorporado)")
    def mark_as_resolved(self, request, queryset):
        total = queryset.update(status=KnowledgeGap.Status.RESOLVED, reviewed_at=timezone.now())
        self.message_user(request, f"{total} brecha(s) marcada(s) como resuelta(s).")

    @admin.action(description="Descartar (fuera de alcance)")
    def mark_as_dismissed(self, request, queryset):
        total = queryset.update(status=KnowledgeGap.Status.DISMISSED, reviewed_at=timezone.now())
        self.message_user(request, f"{total} brecha(s) descartada(s).")
