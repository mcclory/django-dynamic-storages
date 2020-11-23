from test_plus.test import TestCase
from ..factories import TestEncryptedFileFieldModelFactory
from rest_framework.test import APIClient
from django.urls import reverse


class TestSecureContentsView(TestCase):
    def test_retrieve_contents(self):
        c = APIClient()
        tm = TestEncryptedFileFieldModelFactory(storage_target=None)
        user1 = self.make_user("u1", password="P@ssword!")
        c.login(username="u1", password="P@ssword!")
        response = c.get(reverse("secure-file-contents", args=[str(tm.id)]))
        self.assertIsNotNone(response)
        self.assertTrue(response.status_code, 200)
