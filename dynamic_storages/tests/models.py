import base64
import hashlib
import logging
from uuid import uuid4

from cryptography.fernet import Fernet
from django.core.files.storage import default_storage
from django.db import models

from dynamic_storages.conf import settings
from dynamic_storages.fields.dynamic_storage import DynamicStorageFileField, DynamicStorageImageField
from dynamic_storages.fields.encrypted_content import EncryptedFileField, EncryptedImageField
from dynamic_storages.models import AbstractStorageTarget
import random

from django.core.management.utils import get_random_secret_key

log = logging.getLogger(__name__)


class TestStorageTarget(AbstractStorageTarget):
    class Meta(AbstractStorageTarget.Meta):
        abstract = False


class TestBase(models.Model):
    storage_target = models.ForeignKey("TestStorageTarget", on_delete=models.CASCADE)

    class Meta:
        abstract = True


def get_storage(instance):
    if instance:
        return instance.storage_target.storage_backend
    return default_storage


def upload_to(instance, filename):
    prefix = hashlib.md5(str(uuid4()).encode("utf-8")).hexdigest()
    return "{}/{}".format(prefix, filename)


class TestFileStorageModel(TestBase):
    file = DynamicStorageFileField(storage_instance_callable=get_storage, upload_to=upload_to)

    class Meta:
        abstract = False


class TestImageStorageModel(TestBase):
    image = DynamicStorageImageField(storage_instance_callable=get_storage, upload_to=upload_to)

    class Meta:
        abstract = False


def get_fernet(instance, prop_name="key"):
    if not getattr(instance, prop_name, None):
        print("Setting key for fernet in instance")
        setattr(instance, prop_name, Fernet.generate_key())
    return Fernet(getattr(instance, prop_name, None))


class KeyedFieldModel(TestBase):
    key = models.BinaryField(max_length=60, help_text='Generated Fernet key', default=Fernet.generate_key)

    class Meta:
        abstract = True



class TestEncryptedFileFieldModel(KeyedFieldModel, TestBase):
    file = EncryptedFileField(storage_instance_callable=get_storage, fernet=get_fernet, upload_to=upload_to)
    class Meta:
        abstract = False

class TestEncryptedImageFieldModel(KeyedFieldModel, TestBase):
    image = EncryptedImageField(storage_instance_callable=get_storage, fernet=get_fernet, upload_to=upload_to)

    class Meta:
        abstract = False
