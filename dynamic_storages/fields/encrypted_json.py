import json
import logging

from django.core.serializers.json import DjangoJSONEncoder
from fernet_fields import EncryptedTextField

log = logging.getLogger(__name__)


class EncryptedJSONField(EncryptedTextField):
    """JSON dictionary that is encrypted at rest as a text object - based off of the django-fernet-fields EncryptedTextField and useful for storing storage backend configurations"""

    def get_prep_value(self, value):
        ret_val = "{}"
        if value:
            ret_val = json.dumps(value, separators=(",", ":"), cls=DjangoJSONEncoder)
        return ret_val

    def to_python(self, value):
        ret_val = {}
        if isinstance(value, dict):
            ret_val = value
        elif isinstance(value, str):
            ret_val = json.loads(value)
        return ret_val
