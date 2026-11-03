import tempfile
from pathlib import Path
from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db import transaction
from django.db.models import Count
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .models import Document
from .services import indexer
from .services.ai_provider import AIProviderError


def _is_document_admin(user):
    return user.is_authenticated and user.is_active and user.is_staff and user.is_superuser


def _safe_next_url(request, candidate):
    if candidate and url_has_allowed_host_and_scheme(
        candidate,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return candidate
    return reverse("knowledge:document_upload")


def document_login(request):
    next_url = request.POST.get("next") or request.GET.get("next", "")
    if _is_document_admin(request.user):
        return redirect(_safe_next_url(request, next_url))

    error = ""
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user and _is_document_admin(user):
            login(request, user)
            return redirect(_safe_next_url(request, next_url))
        error = "Usuario o contraseña incorrectos, o cuenta sin permisos de administración."

    return TemplateResponse(
        request,
        "knowledge/document_login.html",
        {"next": next_url, "error": error},
    )


@require_POST
def document_logout(request):
    logout(request)
    return redirect("knowledge:document_login")


def document_upload(request):
    if not _is_document_admin(request.user):
        if request.user.is_authenticated:
            return HttpResponseForbidden("No tienes permisos para administrar documentos.")
        login_url = reverse("knowledge:document_login")
        return redirect(f"{login_url}?{urlencode({'next': request.get_full_path()})}")

    context = {
        "active_document_count": Document.objects.filter(is_active=True).count(),
        "recent_documents": Document.objects.annotate(
            upload_chunk_count=Count("chunks")
        ).order_by("-created_at")[:6],
    }

    if request.method == "POST":
        uploaded_file = request.FILES.get("file")
        title = request.POST.get("title", "").strip()
        version = request.POST.get("version", "1").strip()
        source_url = request.POST.get("source_url", "").strip()
        retire_previous = bool(request.POST.get("retire_previous"))

        context.update({"title": title, "version": version, "source_url": source_url})

        if not uploaded_file:
            messages.error(request, "Selecciona un archivo para cargar.")
        elif not title:
            messages.error(request, "El título del documento es obligatorio.")
        else:
            suffix = Path(uploaded_file.name).suffix.lower()
            allowed_suffixes = {".pdf", ".docx", ".txt", ".md"}

            if suffix not in allowed_suffixes:
                messages.error(
                    request,
                    f"Formato no permitido: '{suffix}'. Usa PDF, DOCX, TXT o MD.",
                )
            else:
                temp_path = None
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
                        for chunk in uploaded_file.chunks():
                            temp.write(chunk)
                        temp_path = Path(temp.name)

                    with transaction.atomic():
                        if retire_previous:
                            Document.objects.filter(
                                title=title,
                                is_active=True,
                            ).update(is_active=False)

                        document = Document.objects.create(
                            title=title,
                            version=version,
                            source_url=source_url,
                            is_active=True,
                        )
                        total = indexer.index_from_file(document, temp_path)

                    messages.success(
                        request,
                        f"'{title}' (v{version}) quedó indexado con {total} fragmentos.",
                    )
                    return redirect("knowledge:document_upload")
                except (AIProviderError, ValueError, ImportError) as error:
                    messages.error(request, f"No se pudo indexar el documento: {error}")
                finally:
                    if temp_path and temp_path.exists():
                        temp_path.unlink()

    context["recent_documents"] = Document.objects.annotate(
        upload_chunk_count=Count("chunks")
    ).order_by("-created_at")[:6]
    context["active_document_count"] = Document.objects.filter(is_active=True).count()
    return TemplateResponse(
        request,
        "admin/knowledge/document_upload.html",
        context,
    )
