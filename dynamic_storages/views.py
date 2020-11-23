import logging
import os

import magic
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import View

from .conf import settings

log = logging.getLogger(__name__)


class AbstractSecureFileContents(View):
    """Abstract view to serve as an example for handling returning the contents of an encrypted file"""

    model = None
    url_kwargs = ["pk"]
    file_field = None
    mime_type_field = None

    def get(self, request, *args, **kwargs):
        user_id = request.user
        try:
            query_kwargs = {k: kwargs[k] for k in self.url_kwargs if kwargs.get(k, None)}
            if request.user.is_authenticated:
                doc = get_object_or_404(self.model, **query_kwargs)
                content = getattr(doc, file_field).get_decrypted().read()
                log.info("{} ({}) downloaded by user {}".format(self.model.__class__.__name__, str(doc.id), request.user))
                mime_type = str(getattr(doc, self.mime_type_field, None)) if self.mime_type_field else magic.Magic(mime=True).from_buffer(content)
                return HttpResponse(content, content_type=mime_type)
            else:
                log.warn("Unauthenticated request for {} with kwargs: {}".format(self.model.__name__, query_kwargs))
        except Exception as ex:
            log.warn("Failed to retrieve contents for user {}: {}".format(request.user, ex))
        raise Http404
