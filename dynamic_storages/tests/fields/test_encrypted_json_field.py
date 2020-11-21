from django.test import TestCase

import random
import os
from django.core.management.utils import get_random_secret_key
from ..models import TestEncryptedJSONField
from datetime import datetime
from ..models import TestEncryptedJSONField


class TestEncryptedJsonField(TestCase):
    def test_create(self):
        ejf = TestEncryptedJSONField()
        ejf.save()
        self.assertIsNotNone(ejf.pk)

    def test_save(self):
        ejf = TestEncryptedJSONField()
        for x in range(0, 10):
            ejf.data[x] = datetime.utcnow().isoformat()
        ejf.save()
        ejf.refresh_from_db()
        self.assertIsNotNone(ejf.pk)
        self.assertTrue(isinstance(ejf.data, dict))
