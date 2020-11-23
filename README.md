# Django Dynamic Storages

I'll fill this in with more detail later, but the basic reasoning for this project is that I needed something I could use to extend the already excellent [`django-storages`](https://github.com/jschneier/django-storages) project such that the storage field on any given [`FileField`](https://docs.djangoproject.com/en/3.1/ref/models/fields/#filefield) was a callable I could source a model instance value from. I've also included an abstract class for holding a configuration that stores (securely via [django-fernet-fields](https://github.com/orcasgit/django-fernet-fields)) the access configuration for a given storage backend as well.  

## Goals

I wanted a way to:

* dynamically/at runtime, assign a [`django-storages`](https://github.com/jschneier/django-storages) backend to a given [`FileField`](https://docs.djangoproject.com/en/3.1/ref/models/fields/#filefield) in a model
* dynamically/at runtime, manage the encryption/decryption of the contents of the aforementioned [`FileField`](https://docs.djangoproject.com/en/3.1/ref/models/fields/#filefield)
* Ideally, I'd like to be able to achieve this following idiomatic patterns from [`django-storages`](https://github.com/jschneier/django-storages) in terms of using callable kwargs to achieve this so that the consumer of these components had as much control over details as possible with the least amount of overhead.
    * I took the [`upload_to`](https://docs.djangoproject.com/en/3.1/ref/models/fields/#django.db.models.FileField.upload_to) implementation as inspiration for how to implement the above.

## Components

### Fields

#### `dynamic_storages.fields.dynamic_storage`

`DynamicStorageFileField` and `DynamicStorageImageField` are extensions each of the built-in Django [`FileField`](https://docs.djangoproject.com/en/3.1/ref/models/fields/#filefield) and [`ImageField`](https://docs.djangoproject.com/en/3.1/ref/models/fields/#integerfield) which utilizes the storage backends provided by [django-storages](https://django-storages.readthedocs.io/en/latest/). Rather than setting the `storage` kwarg at the field level, we're using a kwarg we named `storage_instance_callable` to manage the callable function workflow for determining the backend to use. This is, primarily, due to Django 3.0 allowing a callable to be passed in for the `storage` kwarg, however it does not pass the callable function any context - we simply sidestep that issue by using a different kwarg and then use that to set the storage value.


FOr the sake of providing an example, the following is a real-world usage of this process using a callable function which takes the model instance in as an argument. It identifies if a 'team' is attached to the instance and then finds the `TeamStorageTarget` (a separate model derived from `dynamic_storages.models.AbstractStorageTarget`)

```python
def get_storage(instance):
    if instance and getattr(instance, "team", None):
        tst = TeamStorageTarget.for_team(instance.team)
        if tst:
            return tst.storage_backend
    return default_storage
```

#### `dynamic_storages.fields.encrypted_content`

`EncryptedFileField` and `EncryptedImageField` are extensions each of `DynamicStorageFileField` and `DynamicStorageImageField` with the main difference being that these new field definitions encapsulate the process of encrypting and decrypting content for their files at runtime. Two callables are needed to do this, both of which will receive the `instance` object when called:

* `fernet` - the callable assigned to this should return a [`cryptography.fernet.Fernet`](https://cryptography.io/en/latest/fernet.html?highlight=fernet#cryptography.fernet.Fernet) or [`cryptography.fernet.MultiFernet`](https://cryptography.io/en/latest/fernet.html?highlight=fernet#cryptography.fernet.Fernet) for the handling of encryption operations


* `get_url` - the callable assigned to this should return a URL which is configured/designed to decrypt the content and serve it to the end user as appropriate (i.e. security is baked into your views, not into this field directly). An example of what a view might look like for this is located in ['dynamic_storages/views.py'](dynamic_storages/views.py).

In a real-world application, your callable for `get_url` might take multiple values from the instance the file belongs to and construct a url to return:

```python
def file_content_url(instance):
    return reverse_lazy("api:team-files-contents", args=[instance.file.team.slug, instance.team.id, instance.team.file.name.split(".")[-1]])
```

The view that gets exposed for this `get_url` might be a custom action within a Django Rest Framework Viewset such as:

```python
class FileViewSet(viewsets.ModelViewSet):
    """other implementation details not included..."""

    @action(detail=True, methods=["GET"], name="Get File Contents", url_path="contents.<str:file_ext>")
    def contents(self, request, **kwargs):
        user = request.user
        try:
            if request.user.is_authenticated():
                team = get_object_or_404(Team, slug=kwargs.get("parent_lookup_team__slug"))
                file_ext = self.kwargs["file_ext"]
                if user_can_access_team(user, team):
                    f = get_object_or_404(File, team=team, pk=kwargs["pk"])
                    content = f.file.get_decrypted().read()
                    return HttpResponse(
                        content,
                        content_type=magic.Magic(mime=True).from_buffer(content),
                    )
                else:
                    log.warn("User {} is not allowed to access resources for team {}".format(user.username, team.name))
            else:
                log.warn("User is not authenticated for request to file with {}".format(self.kwargs))
        except Exception as ex:
            log.warn("Failed to get property for request: {}".format(ex))
        raise Http404
```

#### `dynamic_storages.fields.encrypted_json`

The `EncryptedJSONField` is meant to be useful in handling the storage of things like storage credentials within a database. It was useful in our testing and we've found that even though it follows an older pattern in the Django community around JSONFields (given that Django 3 has them built in now), this setup serves well for credential storage.  It leverages the [`django-fernet-fields`](https://github.com/orcasgit/django-fernet-fields) [`EncryptedTextField`](https://github.com/orcasgit/django-fernet-fields/blob/master/fernet_fields/fields.py#L109) as its storage medium and we're simply marshaling it back and forth from dictionary to string.  


### Other Stuff

### Running Tests

This project has test-level models... as such, to run the tests built into this project, you'll want to run Django from the `./runtests.py` script which simply adds the test application to the `INSTALLED_APPS` list.

```bash
./runtests.py test
```


## To-Do

* [ ] Update the `.models.AbstractStorageTarget` model to include credential checking
* [ ] Create async task for handling credential checking periodically for `AbstractStorageTarget`-based storage
* [ ] look into further extending `django-storages` to handle google drive (since it already supports dropbox)
* [ ] simplify and validate usage of the generic ~`AbstractSecureFileContents`~ `GenericFileContentsView` view
* [X] write more tests around the `default_storage` provider (`0.4.1`)

## Revisions


* `0.5.2` (Mon Nov 23 01:00:08 PM PST 2020) - so I had to take a dependency on [django-rest-framework](https://www.django-rest-framework.org/) but it made the generic views for retrieving encrypted content a lot easier to deal with. New tests and tweaks to the generic views and we're in business!
* `0.5.1` (Mon Nov 23 12:!5:14 PM PST 2020) - Renaming Abstract views to 'Generic' and layering them in so that they can be extended/used more easily
* `0.5.0` (Mon Nov 23 11:42:33 AM PST 2020) - fixing formatting, ran `isort` and added some logging to the `AbstractStorageTarget` process which constructs the backend classes.
* `0.4.5` (Mon Nov 23 11:24:18 AM PST 2020) - updates to generic/abstract view to pull `mime_type` from a model field if it's specified... adding common logger for all components.
* `0.4.2` (Fri Nov 20 07:04:43 PM PST 2020) - wrote more tests around storage providers, object create (for file and img fields) as well as some tidying up around the edges
* `0.4.0` (Mon Nov 16 09:50:48 AM PST 2020) - readme updates, documentation fixes, more clarity/examples, added some todo's
* `0.3.8` (Mon Nov 16 09:22:41 AM PST 2020) - docstring updates and some changes to the order of operations re: generating a download url for a file via callables
* `0.3.7` (Mon Nov 16 09:05:32 AM PST 2020) - Fixing typo
* `0.3.6` (Fri Nov 13 10:01:38 AM PST 2020) - consistency issues with get_url call again... mirroring process from the fernet setup
* `0.3.5` (Thu Nov 12 03:53:03 PM PST 2020) - fixes to my `get_url` stuff - dumb misses
* `0.3.4` (Thu Nov 12 11:42:21 AM PST 2020) - minor update to allow for a callable function to be passed in for an `EncryptedFileField` so that you can externally control the view/url that needs to be used to get the contents of this file.
