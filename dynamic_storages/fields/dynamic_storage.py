import logging
from django.db.models.fields.files import FieldFile, FileField, ImageField
from django.core.files.images import ImageFile

log = logging.getLogger(__name__)


class FileFieldMixin(object):
    def pre_save(self, model_instance, add):
        if getattr(self, "_storage_callable", None):
            if callable(self._storage_callable):
                self.storage = self._storage_callable(model_instance)
        return super().pre_save(model_instance, add)


class DynamicStorageFieldFile(FieldFile):
    """FieldFile implementation for dynamically setting the storage provider for the file at runtime based on a callable passed into the field definition"""

    def __init__(self, instance, field, name):
        if getattr(field, "storage_instance_callable", None):
            storage = field.storage_instance_callable(instance)
            log.info("Setting storage for this field to {}".format(storage))
            field.storage = storage
        super().__init__(instance, field, name)


class DynamicStorageFileField(FileFieldMixin, FileField):
    """File field implementation for dynamically setting the storage provider for the file to be stored/retrieved at runtime based on a callable passed into this field definition for the `storage` kwarg"""

    attr_class = DynamicStorageFieldFile

    def __init__(self, *args, **kwargs):
        if "storage_instance_callable" in kwargs and kwargs.get("storage_instance_callable"):
            self.storage_instance_callable = kwargs.pop("storage_instance_callable")
        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        if getattr(self, "storage_instance_callable", None):
            if callable(self.storage_instance_callable):
                self.storage = self.storage_instance_callable(model_instance)
        return super().pre_save(model_instance, add)


class DynamicStorageImageFieldFile(ImageFile, DynamicStorageFieldFile):
    def delete(self, save=True):
        if hasattr(self, "_dimensions_cache"):
            del self._dimensions_cache
        super().delete(save)


class DynamicStorageImageField(DynamicStorageFileField, ImageField):
    attr_class = DynamicStorageImageFieldFile
