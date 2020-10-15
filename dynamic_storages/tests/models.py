from dynamic_storages.models import AbstractStorageTarget
from django.db import models
from dynamic_storages.db.fields import DynamicStorageFileField
from django.core.files.storage import default_storage


class TestStorageTarget(AbstractStorageTarget):
    class Meta(AbstractStorageTarget.Meta):
        abstract = False


def get_storage(instance=None):
    if instance:
        return instance.storage_target.storage_backend
    return default_storage


class TestFileStorageModel(models.Model):
    file = DynamicStorageFileField(storage=get_storage)
    storage_target = models.ForeignKey("TestStorageTarget", on_delete=models.CASCADE)
