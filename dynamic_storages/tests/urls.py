"""_test_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from .models import TestEncryptedFileFieldModel
from ..views import GenericFileContentsView, GenericSecureFileContentsView


class FileContentsView(GenericFileContentsView):
    queryset = TestEncryptedFileFieldModel.objects.all()
    file_field = "file"
    mime_type_field = None


class SecureFileContentsView(GenericSecureFileContentsView):
    queryset = TestEncryptedFileFieldModel.objects.all()
    file_field = "file"
    mime_type_field = None


urlpatterns = [
    path("files/<pk>/content/", FileContentsView.as_view({"get": "retrieve"}), name="file-contents"),
    path("files/<pk>/content/secure/", SecureFileContentsView.as_view({"get": "retrieve"}), name="secure-file-contents"),
]
