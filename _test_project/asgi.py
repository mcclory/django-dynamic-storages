"""
ASGI config for _test_project project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os

# settings.py
from dotenv import load_dotenv

load_dotenv()

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "_test_project.settings")

application = get_asgi_application()
