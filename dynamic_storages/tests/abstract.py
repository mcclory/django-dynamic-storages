import factory
import os
import json
import base64
from dynamic_storages.models.mappings import LAST_STATUS_CHOICES, STORAGE_PROVIDER_MAP
from functools import partial
from faker import Faker
import logging

log = logging.getLogger(__name__)

fake = Faker()


def get_config(key, **kwargs):
    log.debug("Getting config for {}".format(key))
    ret_val = {}
    if key.lower() == "alc":
        pass
    elif key.lower() in ["as", "azure"]:
        ret_val = {
            "account_key": kwargs.get(
                "account_key",
                os.getenv(
                    "TEST_AZURE_ACCOUNT_KEY",
                ),
            ),
            "account_name": kwargs.get(
                "account_name",
                os.getenv("TEST_AZURE_ACCOUNT_NAME"),
            ),
            "overwrite_files": bool(kwargs.get("overwrite_files", "True")),
            "azure_container": kwargs.get(
                "azure_container",
                os.getenv("TEST_AZURE_CONTAINER"),
            ),
        }
    elif key.lower() == "dropbox":
        ret_val = {
            "oauth2_access_token": kwargs.get("oauth2_access_token", os.getenv("TEST_DBS_OAUTH2_TOKEN")),
            "root_path": kwargs.get("root_path", os.getenv("TEST_DBS_ROOT_PATH")),
        }
    elif key.lower() == "ftp":
        ret_val = {
            "location": "ftp://{}:{}@{}:{}/".format(
                kwargs.get("username", os.getenv("TEST_FTP_USER_NAME")),
                kwargs.get("password", os.getenv("TEST_FTP_USER_PASS")),
                kwargs.get("host", os.getenv("TEST_FTP_HOST")),
                kwargs.get("port", os.getenv("TEST_FTP_PORT")),
            )
        }
    elif key.lower() == "gcloud":
        ret_val = {
            "bucket_name": kwargs.get(
                "bucket_name",
                os.getenv("TEST_GCS_BUCKET_NAME"),
            ),
            "credentials": json.loads(base64.b64decode(os.getenv("TEST_GCS_SERVICE_ACCOUNT_JSON", "{}"))),
        }
    elif key.lower() == "do":
        ret_val = {
            "access_key": kwargs.get("access_key", os.getenv("TEST_DO_ACCESS_KEY")),
            "secret_key": kwargs.get("secret_key", os.getenv("TEST_DO_SECRET_KEY")),
            "bucket_name": kwargs.get(
                "bucket_name",
                os.getenv("TEST_DO_BUCKET_NAME"),
            ),
            "region_name": kwargs.get("region_name", os.getenv("TEST_DO_REGION_NAME", "sfo2")),
            "default_acl": kwargs.get("default_acl", "private"),
        }
    elif key.lower() in ["s3b", "aws", "s3boto3"]:
        ret_val = {
            "access_key": kwargs.get("access_key", os.getenv("TEST_AWS_ACCESS_KEY")),
            "secret_key": kwargs.get("secret_key", os.getenv("TEST_AWS_SECRET_KEY")),
            "file_overwrite": kwargs.get("file_overwrite", True),
            "bucket_name": kwargs.get(
                "bucket_name",
                os.getenv("TEST_AWS_BUCKET_NAME", "introsepect-data-django-test"),
            ),
            "region_name": kwargs.get("region_name", os.getenv("TEST_AWS_REGION_NAME")),
            "default_acl": kwargs.get("default_acl", "private"),
        }
    elif key.lower() == "sftp":
        SSH_KEY_PATH = os.path.join(TEST_DATA_BASE_DIR, "sftp")
        with open(os.path.join(SSH_KEY_PATH, "sftp-test"), "r") as f:
            ssh_private_key = f.read()

        ret_val = {
            "host": kwargs.get("host", os.getenv("TEST_SFTP_HOST")),
            "params": {
                "port": int(kwargs.get("port", os.getenv("TEST_SFTP_PORT"))),
                "username": kwargs.get("username", os.getenv("TEST_SFTP_USER_NAME")),
                "password": kwargs.get("password", os.getenv("TEST_SFTP_USER_PASS")),
                "pkey": ssh_private_key,
            },
            "interactive": None,
            "file_mode": None,
            "dir_mode": None,
            "uid": None,
            "gid": None,
            "known_host_file": None,
            "root_path": None,
            "base_url": None,
        }
    log.debug("Config for {} is {}".format(key, ret_val))
    return ret_val


class AbstractStorageTargetFactory(factory.django.DjangoModelFactory):
    name = factory.LazyFunction(fake.catch_phrase)
    description = factory.LazyFunction(partial(fake.paragraph, 3))
    provider = factory.fuzzy.FuzzyChoice([x for x in STORAGE_PROVIDER_MAP.keys()], getter=lambda c: c)
    config = factory.LazyAttribute(lambda o: get_config(o.provider))
    last_status = factory.fuzzy.FuzzyChoice([x for x in LAST_STATUS_CHOICES], getter=lambda c: c[0])

    class Meta:
        abstract = True
