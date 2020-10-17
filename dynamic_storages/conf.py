import os

from appconf import AppConf
from django.conf import settings


class DynamicStoragesAppConf(AppConf):
    DOWNLOAD_REQUIRE_LOGIN = bool(os.getenv("DS_DOWNLOAD_REQUIRE_LOGIN", True))
    DOWNLOAD_URL_ARG_NAMES = os.getenv("DS_DOWNLOAD_URL_ARG_NAMES", "pk").split(",")
    DOWNLOAD_URL_KWARG_NAMES = os.getenv("DS_DOWNLOAD_URL_KWARG_NAMES", "pk").split(",")
    DOWNLOAD_INCLUDE_FILE_EXT = bool(os.getenv("DS_DOWNLOAD_INCLUDE_FILE_EXT", True))
    DOWNLOAD_URL_NAME = os.getenv("DOWNLOAD_URL_NAME", "")  # encrypted_file_download

    class Meta:
        prefix = "DS"
