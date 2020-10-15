from django.apps import AppConfig


class DynamicStoragesConfig(AppConfig):
    name = "dynamic_storages"
    label = "Dynamic Storages"
    verbose_name = "Dynamic Storages"

    def ready(self):
        pass
