import glob
import os
import random

from django.core.management.utils import get_random_secret_key
from django.test import TestCase

from .. import TEST_FILES_DIR, TEST_IMAGES_DIR
from ..models import TestEncryptedFileFieldModel, TestEncryptedImageFieldModel
from .util import open_file


class TestEncryptedFileField(TestCase):
    def setUp(self):
        self.files = list(glob.glob(os.path.join(TEST_FILES_DIR, "*")))

    def test_create(self):
        f = TestEncryptedFileFieldModel()
        f.file.save(*open_file(self.files.pop()), save=True)
        f.save()
        self.assertIsNotNone(f.pk)
        return f


class TestEncryptedImageField(TestCase):
    def setUp(self):
        self.files = list(glob.glob(os.path.join(TEST_IMAGES_DIR, "*")))

    def test_create(self):
        img = TestEncryptedImageFieldModel()
        img.image.save(*open_file(self.files.pop()), save=True)
        img.save()
        self.assertIsNotNone(img.pk)
        return img
