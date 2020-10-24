import logging
from io import BytesIO

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from django.core.files.images import ImageFile
from django.db.models.fields.files import FieldFile, FileField, ImageField
from django.urls import reverse

from ..conf import settings
from .dynamic_storage import (DynamicStorageFieldFile, DynamicStorageFileField,
                              DynamicStorageImageField,
                              DynamicStorageImageFieldFile, FileFieldMixin)

log = logging.getLogger(__name__)


class EncryptedFile(BytesIO):
    def __init__(self, content, fernet):
        if content:
            BytesIO.__init__(self, fernet.encrypt(content.read()))
        else:
            BytesIO.__init__(self, None)


class DecryptedFile(BytesIO):
    def __init__(self, content, fernet):
        if content:
            if isinstance(content, EncryptedFieldFile):
                content = content.read()
            BytesIO.__init__(self, fernet.decrypt(content))
        else:
            BytesIO.__init__(self, None)


class EncryptedFieldFile(DynamicStorageFieldFile):
    def __init__(self, instance, field, name, **kwargs):
        self.fernet = getattr(field, "fernet", None)
        super().__init__(instance, field, name)
        if callable(self.fernet):
            self.fernet = self.fernet(instance) if self.fernet and callable(self.fernet) else self.fernet
        if not self.fernet:
            raise RuntimeError("Encryption Fernet details not provided for this instance of a EncryptedFieldFile")

    @property
    def fernet(self):
        return getattr(self, "_fernet", None)

    @fernet.setter
    def fernet(self, val):
        self._fernet = val

    def _get_url(self):
        if settings.DS_DOWNLOAD_URL_NAME:
            url_args = []
            for k in settings.DS_DOWNLOAD_URL_ARG_NAMES:
                val = str(getattr(self.instance, k, None))
                if val:
                    url_args.append(val)
            return reverse(settings.DS_DOWNLOAD_URL_NAME, args=url_args)
        return None

    def get_decrypted(self):
        return DecryptedFile(self.open('rb').read(), self.fernet)

    url = property(_get_url)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.fernet:
            kwargs["fernet"] = self.fernet
        return name, path, args, kwargs

    def save(self, name, content, save=True):
        return DynamicStorageFieldFile.save(self, name, EncryptedFile(content, self.fernet), save=save)

    save.alters_data = True


class EncryptedFileField(DynamicStorageFileField):
    attr_class = EncryptedFieldFile

    def __init__(self, *args, **kwargs):
        self.fernet = kwargs.pop("fernet", None)
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.fernet:
            kwargs["fernet"] = self.fernet
        return name, path, args, kwargs


class EncryptedImageFieldFile(ImageFile, EncryptedFieldFile):
    def delete(self, save=True):
        if hasattr(self, "_dimensions_cache"):
            del self._dimensions_cache
        super().delete(save)

    def save(self, name, content, save=True):
        return DynamicStorageImageFieldFile.save(self, name, EncryptedFile(content, self.fernet), save=save)


class EncryptedImageField(DynamicStorageImageField):
    attr_class = EncryptedImageFieldFile

    def __init__(self, *args, **kwargs):
        fernet = kwargs.pop("fernet", None)
        super().__init__(*args, **kwargs)
        self.fernet = fernet
