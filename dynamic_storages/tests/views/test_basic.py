from test_plus.test import TestCase
from ..factories import TestEncryptedFileFieldModelFactory
from rest_framework.test import APIClient
from django.urls import reverse


class TestBasicContentsView(TestCase):
    def test_retrieve_contents(self):
        c = APIClient()
        tm = TestEncryptedFileFieldModelFactory(storage_target=None)
        response = c.get(reverse("file-contents", args=[str(tm.id)]))
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)
