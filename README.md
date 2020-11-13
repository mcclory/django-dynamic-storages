# Django Dynamic Storages

I'll fill this in with more detail later, but the basic reasoning for this project is that I needed something I could use to extend the already excellent [django-storages](https://github.com/jschneier/django-storages) project such that the storage field on any given `FileField` was a callable I could source a model instance value from. I've also included an abstract class for holding a configuration that stores (securely via [django-fernet-fields](https://github.com/orcasgit/django-fernet-fields)) the access configuration for a given storage backend as well.  

## Revisions

* `0.3.6` (Fri Nov 13 10:01:38 AM PST 2020) - consistency issues with get_url call again... mirroring process from the fernet setup
* `0.3.5` (Thu Nov 12 03:53:03 PM PST 2020) - fixes to my `get_url` stuff - dumb misses
* `0.3.4` (Thu Nov 12 11:42:21 AM PST 2020) - minor update to allow for a callable function to be passed in for an `EncryptedFileField` so that you can externally control the view/url that needs to be used to get the contents of this file.
