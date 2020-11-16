import os

import magic
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import View

from .conf import settings


class AbstractSecureFileContents(View):
    """Abstract view to serve as an example for handling returning the contents of an encrypted file"""

    model = None
    url_kwargs = []
    file_field = None

    def get(self, request, *args, **kwargs):
        user_id = request.user
        try:
            query_kwargs = {k: kwargs.get(k) for k in url_kwargs if kwargs.get(k)}
            if request.user.is_authenticated:
                doc = get_object_or_404(self.model, **query_kwargs)
                content = getattr(doc, file_field).get_decrypted().read()
                return HttpResponse(content, content_type=magic.Magic(mime=True).from_buffer(content))
            else:
                log.warn("Unauthenticated request for {} with kwargs: {}".format(self.model.__name__, query_kwargs))
        except Exception as ex:
            log.warn("Failed to get property for request: {}".format(ex))
        raise Http404
