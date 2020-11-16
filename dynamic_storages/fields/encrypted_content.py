import logging
from io import BytesIO

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from django.core.files.images import ImageFile
from django.db.models.fields.files import FieldFile, FileField, ImageField
from django.urls import reverse

from ..conf import settings
from .dynamic_storage import DynamicStorageFieldFile, DynamicStorageFileField, DynamicStorageImageField, DynamicStorageImageFieldFile, FileFieldMixin

log = logging.getLogger(__name__)


class EncryptedFile(BytesIO):
    """Wrapper class which encrypts the content supplied with the fernet specified on initialization"""

    def __init__(self, content, fernet):
        if content and hasattr(content, "read"):
            content = content.read()
        if content:
            BytesIO.__init__(self, fernet.encrypt(content))
        else:
            BytesIO.__init__(self, content)


class DecryptedFile(BytesIO):
    """Wrapper class around `io.BytesIO` that augments the initialization of the class to decrypt contents if a fernet is passed in to the constructor"""

    def __init__(self, content, fernet):
        if content and hasattr(content, "read"):
            content = content.read()
        if content:
            BytesIO.__init__(self, fernet.decrypt(content))
        else:
            BytesIO.__init__(self, content)


class EncryptedFieldFile(DynamicStorageFieldFile):
    """`EncryptedFileField` extends the DynamicStorageFieldFile allowing for files stored to be encrypted based on model instance-level properties"""

    def __init__(self, instance, field, name, **kwargs):
        self.fernet = getattr(field, "fernet", None)
        self._get_url = getattr(field, "get_url", None)
        super().__init__(instance, field, name)
        if callable(self.fernet):
            log.debug("EncryptedFieldFile init - fernet {} is callable".format(self.fernet))
            self.fernet = self.fernet(instance)
        if not self.fernet:
            raise RuntimeError("Encryption Fernet details not provided for this instance of a EncryptedFieldFile")
        if callable(self._get_url):
            log.debug("EncryptedFieldFile init - _get_url {} is callable".format(self._get_url))
            self.model_instance = instance

    @property
    def fernet(self):
        """Retrieve the fernet/multifernet associated with this instance of an `EncryptedFieldFile`"""
        return getattr(self, "_fernet", None)

    @fernet.setter
    def fernet(self, val):
        """Set the fernet/multifernet associated with this instance of an `Encrypted FieldFile`"""
        self._fernet = val

    def get_decrypted(self):
        """method decrypts bytes from file if a fernet is provided for this instance of an `EncryptedFieldFile`"""
        if self.fernet:
            log.debug("Fernet type is {}".format(type(self.fernet)))
            return DecryptedFile(self.open("rb"), self.fernet)
        else:
            return BytesIO(self.open("rb").read())

    @property
    def url(self):
        """Override the default url generation for files to allow for it to be decrypted before serving to the user"""
        return self._get_url(self.model_instance) if getattr(self, "model_instance", None) else super().url

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.fernet:
            kwargs["fernet"] = self.fernet
        return name, path, args, kwargs

    def save(self, name, content, save=True):
        return DynamicStorageFieldFile.save(self, name, EncryptedFile(content, self.fernet), save=save)

    save.alters_data = True


class EncryptedFileField(DynamicStorageFileField):
    """Django-level `FileField` extended implementation that allows for individual encryption keying on a per-model instance level"""

    attr_class = EncryptedFieldFile

    def __init__(self, *args, **kwargs):
        self.fernet = kwargs.pop("fernet", None)
        self.get_url = kwargs.pop("get_url", None)
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.fernet:
            kwargs["fernet"] = self.fernet
        return name, path, args, kwargs


class EncryptedImageFieldFile(ImageFile, EncryptedFieldFile):
    """`FieldFile` implementation for handling image fields with the ability to encrypt on a per-model instance basis"""

    def delete(self, save=True):
        if hasattr(self, "_dimensions_cache"):
            del self._dimensions_cache
        super().delete(save)

    def save(self, name, content, save=True):
        return DynamicStorageImageFieldFile.save(self, name, EncryptedFile(content, self.fernet), save=save)


class EncryptedImageField(DynamicStorageImageField):
    """Per Django pattern, a model field specific to handling Images that allows for individual encryption keying on a per-model instance level"""

    attr_class = EncryptedImageFieldFile

    def __init__(self, *args, **kwargs):
        self.fernet = kwargs.pop("fernet", None)
        self.get_url = kwargs.pop("get_url", None)
        super().__init__(*args, **kwargs)
