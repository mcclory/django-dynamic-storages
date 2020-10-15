from django.test import TestCase
from .factories import TestStorageTargetFactory, TestFileStorageModelFactory


class TestStorageTargetFactoryTestCase(TestCase):
    def test_gcs(self):
        tstf = TestStorageTargetFactory(provider="gcloud")
        self.assertIsNotNone(tstf.pk)

    def test_aws(self):
        tstf = TestStorageTargetFactory(provider="s3boto3")
        self.assertIsNotNone(tstf.pk)

    def test_azure(self):
        tstf = TestStorageTargetFactory(provider="azure")
        self.assertIsNotNone(tstf.pk)


class TestFileStorageModelFactorytestCase(TestCase):
    def test_gcs(self):
        tstf = TestStorageTargetFactory(provider="gcloud")
        tfsmf = TestFileStorageModelFactory(storage_target=tstf)
        self.assertIsNotNone(tfsmf.pk)
        self.assertIsNotNone(tfsmf.file.url)

    def test_aws(self):
        tstf = TestStorageTargetFactory(provider="s3boto3")
        tfsmf = TestFileStorageModelFactory(storage_target=tstf)
        self.assertIsNotNone(tfsmf.pk)
        self.assertIsNotNone(tfsmf.file.url)

    def test_azure(self):
        tstf = TestStorageTargetFactory(provider="azure")
        tfsmf = TestFileStorageModelFactory(storage_target=tstf)
        self.assertIsNotNone(tfsmf.pk)
        self.assertIsNotNone(tfsmf.file.url)
