import logging
from uuid import uuid4

from django.core.files.storage import default_storage
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from google.oauth2 import service_account

from ..fields.encrypted_json import EncryptedJSONField
from ..utils import log
from .mappings import LAST_STATUS_CHOICES, STORAGE_PROVIDER_MAP


class AbstractStorageTarget(models.Model):
    """Abstract implementation of a storage target which includes access details for how to interact with the downstream object storage system"""

    id = models.UUIDField(
        default=uuid4,
        primary_key=True,
        help_text=_("UUID identifying this objects"),
    )
    name = models.CharField(
        max_length=150,
        db_index=True,
        help_text=_("Name of this object"),
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text=_("Description of this object"),
    )
    last_checked = models.DateTimeField(
        null=True,
        blank=True,
        editable=False,
        help_text=_("Timestamp identifying when this storage provider was last checked"),
    )
    last_status = models.CharField(
        max_length=1,
        default="u",
        editable=False,
        choices=LAST_STATUS_CHOICES,
        help_text=_("Flag indiciating what the last status check result was"),
    )
    status_detail = models.TextField(
        blank=True,
        null=True,
        editable=False,
        help_text=_("Status details from last status check"),
    )
    provider = models.CharField(
        max_length=8,
        default="gcloud",
        choices=((k, v.get("name")) for k, v in STORAGE_PROVIDER_MAP.items()),
        help_text=_("Specific storage provider this target utilizes - generally an object storage solution of some sort"),
    )
    config = EncryptedJSONField(
        default=dict,
        blank=True,
        null=True,
        help_text=_("Key/value pairs to pass to the storage provider when initializing the storage backend"),
    )
    created = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text=_("Timestamp indicating when this object was created"),
    )
    modified = models.DateTimeField(
        auto_now=True,
        db_index=True,
        help_text=_("Timestamp indicating when this object was last updated"),
    )
    as_of = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        help_text=_("Timestamp that this storage provider should be used as of"),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._storage_provider = None

    @classmethod
    def as_of(cls, timestamp):
        return cls.objects.filter(as_of__lte=timestamp or timezone.now())

    def __self__(self):
        return "{} - {}".format(self.name, self.get_storage_provider_display())

    def __repr__(self):
        return str(self.id)

    @property
    def storage_backend(self):
        """Property that should be used when assigning a DynamicStorageFileField's `storage` property at runtime"""
        # anything that's in the map that has a class object referenced, try to build it, otherwise assume all others should return default...
        if self.provider in [k for k, v in STORAGE_PROVIDER_MAP.items() if v.get("class", None)]:
            if not getattr(self, "_storage_backend", None):
                create_class = STORAGE_PROVIDER_MAP[self.provider]["class"]
                create_kwargs = getattr(self, "config", {}).copy()
                if self.provider == "gcloud":
                    log.debug("creds: {}".format(create_kwargs.get("credentials", {})))
                    create_kwargs["credentials"] = service_account.Credentials.from_service_account_info(create_kwargs.pop("credentials", {}))
                    log.debug("Storage Target - storage_backend - created credentials object for Google APIs from credential json provided.")
                if self.provider == "do":
                    create_kwargs["addressing_style"] = "path"
                    if not create_kwargs.get("region_name"):
                        create_kwargs["region_name"] = "SFO1"
                        log.debug("Storage Target - storage_backend - set region_name to SFO1 for DigitalOcean as no other value was set")
                    create_kwargs["endpoint_url"] = "https://{}.digitaloceanspaces.com".format(create_kwargs.get("region_name", "SFO1"))
                elif self.provider == "s3boto3":
                    create_kwargs["default_acl"] = create_kwargs.get("default_acl", "bucket-owner-full-control")
                    log.debug("Storage Target - storage_backend - set default_acl to {}".format(create_kwargs["default_acl"]))
                self._storage_backend = create_class(**create_kwargs)
                log.debug("Storage Target - storage_backend - set local _storage_backend value for {}".format(self.provider))
            if getattr(self, "_storage_backend", None):
                return self._storage_backend
            else:
                raise RuntimeError(
                    "Storage Target - storage_backend - provider is not default and self._storage_provider has not been set - something is wrong with the storage backend construction/init process"
                )
        else:
            log.debug("Storage Target - storage_backend - No storage provider can be determined from this model, returnin the Django `default_storage` backend")
            return default_storage

    def _check_credentials(self):
        pass

    class Meta:
        abstract = True
        verbose_name = _("Storage Target")
        verbose_name_plural = _("Storage Targets")
