import base64
import json
import logging
import os
import string
from datetime import timedelta
from functools import partial

import factory
import factory.django
import factory.fuzzy
from django.core.files.base import ContentFile
from django.utils import timezone
from django.utils.text import slugify
from faker import Faker

from dynamic_storages.models.mappings import LAST_STATUS_CHOICES, STORAGE_PROVIDER_MAP

from .models import TestEncryptedFileFieldModel, TestEncryptedImageFieldModel, TestFileStorageModel, TestImageStorageModel, TestStorageTarget, get_fernet
from .abstract import AbstractStorageTargetFactory

log = logging.getLogger(__name__)

fake = Faker()


class TestStorageTargetFactory(AbstractStorageTargetFactory):
    class Meta:
        model = TestStorageTarget


def gen_file():
    return ContentFile(fake.binary(), name=fake.file_name())


class TestFileStorageModelFactory(factory.django.DjangoModelFactory):
    storage_target = factory.SubFactory(TestStorageTargetFactory)
    file = factory.django.FileField(from_func=gen_file)

    class Meta:
        model = TestFileStorageModel


class TestImageStorageModelFactory(factory.django.DjangoModelFactory):
    storage_target = factory.SubFactory(TestStorageTargetFactory)
    image = factory.django.ImageField()

    class Meta:
        model = TestImageStorageModel


class TestEncryptedFileFieldModelFactory(factory.django.DjangoModelFactory):
    storage_target = factory.SubFactory(TestStorageTargetFactory)
    file = factory.django.FileField(from_func=gen_file)

    class Meta:
        model = TestEncryptedFileFieldModel


class TestEncryptedImageFieldModelFactory(factory.django.DjangoModelFactory):
    storage_target = factory.SubFactory(TestStorageTargetFactory)
    image = factory.django.ImageField()

    class Meta:
        model = TestEncryptedImageFieldModel
