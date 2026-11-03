from django.urls import path

from . import views

app_name = "knowledge"

urlpatterns = [
    path("ingresar/", views.document_login, name="document_login"),
    path("documentos/", views.document_upload, name="document_upload"),
    path("salir/", views.document_logout, name="document_logout"),
]
