import logging
import os

import magic
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, mixins

from .conf import settings

log = logging.getLogger(__name__)


class GenericFileContentsView(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """Generic view to serve as an example for handling returning the contents of an encrypted file"""

    authentication_classes = [SessionAuthentication, BasicAuthentication]

    file_field = None
    mime_type_field = None

    def retrieve(self, request, *args, **kwargs):
        try:
            obj = self.get_object()
            content = getattr(obj, self.file_field).get_decrypted().read()
            mime_type = str(getattr(obj, self.mime_type_field, None)) if self.mime_type_field else magic.Magic(mime=True).from_buffer(content)
            log.info("() ({}) retrieved for download by user {}".format(obj.__class__.__name__, str(obj.id), request.user))
            return HttpResponse(content, content_type=mime_type)
        except Exception as ex:
            log.warn("Failed to retrieve contents for user {}: {}".format(request.user, ex))
        raise Http404


class GenericSecureFileContentsView(GenericFileContentsView):
    """Generic view to serve as an example for handling returning the contents of an encrypted file which requires a user to be authenticated"""

    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
