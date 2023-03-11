import os

# settings.py
from dotenv import load_dotenv

load_dotenv()

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "_test_project.settings")

application = get_asgi_application()
