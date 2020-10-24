from django.test import TestCase

from ..factories import (TestEncryptedFileFieldModelFactory,
                        TestEncryptedImageFieldModelFactory,
                        TestFileStorageModelFactory,
                        TestImageStorageModelFactory, TestStorageTargetFactory)

from ..models import TestEncryptedFileFieldModel, TestEncryptedImageFieldModel
import random

from django.core.management.utils import get_random_secret_key
