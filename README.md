# Django Dynamic Storages

I'll fill this in with more detail later, but the basic reasoning for this project is that I needed something I could use to extend the already excellent [django-storages](https://github.com/jschneier/django-storages) project such that the storage field on any given `FileField` was a callable I could source a model instance value from. I've also included an abstract class for holding a configuration that stores (securely via [django-fernet-fields](https://github.com/orcasgit/django-fernet-fields)) the access configuration for a given storage backend as well.  
