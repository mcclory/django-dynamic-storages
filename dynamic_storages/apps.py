from django.apps import AppConfig


class DynamicStoragesConfig(AppConfig):
    name = "dynamic_storages"
    label = "dynamic_storages"
    verbose_name = "Dynamic Storages"

    def ready(self):
        pass
