Title: Django : Accelerate the collection of static files on AWS S3
Date: 2024-02-23 18:00
Id: 0004
Slug: django-accelerate-collectstatic-on-aws-s3
Lang: en
Category: development
Tags: django, aws
Summary: Our strategy for making the collection of static files from a Django application on AWS S3 much faster and more economical.

# The problem

When we store the static files of a Django application on AWS S3, we generally use [django-storages](https://pypi.org/project/django-storages/) and [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html).

In this configuration, the collection of static files can be [particularly slow](https://github.com/jschneier/django-storages/issues/904). The reason for this is simple: all existing files are downloaded before being compared to determine whether or not they should be (re-)uploaded.

[Collectfast](https://pypi.org/project/Collectfast/) offers a solution, but it doesn't work when file names contain hashes, which is the case when [Whitenoise](https://pypi.org/project/whitenoise/) (for example), is part of the stack.

Here's how we've improved static file collection to make it up to 50x faster in this configuration.

# The approach

The idea comes from [the approach proposed here](https://github.com/jschneier/django-storages/issues/904#issuecomment-1248660983) which consists of : 

1. collect static files locally
2. then synchronise them on S3

The two disadvantages of this method are as follows:

- You have to delete `django-storages` and go back to a traditional local backend storage.
- You have to install and use the AWS cli for synchronisation.

We have therefore adapted this approach to counter these disadvantages, by overloading the `collectstatic` command so that it follows the following process:

1. temporarily replace the storage backend with a classic local filesystem backend such as Django's `ManifestStaticFilesStorage` or Whitenoise's `CompressedManifestStaticFilesStorage`,
2. run the native `collectstatic` (locally),
3. detect the differences between the local static files just collected and those existing on S3,
4. upload the files that need to be uploaded

# The solution

The structure:

```python
from django.contrib.staticfiles.management.commands.collectstatic import (
    Command as DjangoCollectStaticCommand,
)


class Command(DjangoCollectStaticCommand):

    @contextmanager
    def _force_file_system_storage(self):
        """
        Replaces S3 static_files storage configured in settings
        by whitenoise (a full-featured local storage with compression and manifest)
        """
    
    def _detect_differences(self) -> list(str):
        """
        Compares local and remote manifest and returns differences
        """
 
    def _sync_files_to_s3(self, diff_manifest_files: []):
        """
        Iterates on files collected locally and (re-upload) them if needed
        """

    def handle(self, **options):
        """
        Overrides django's native command to collect static files locally and
        sync files to S3 afterwards
        """
        with self._force_file_system_storage():
            ret = super().handle(**options)
        self._detect_differences()
        self._sync_files_to_s3()
        return ret
```

The context manager:

```python
    @contextmanager
    def _force_file_system_storage(self):
        """
        Replaces S3 static_files storage configured in settings
        by whitenoise (a full-featured local storage with compression and manifest)
        """
        self._original_storage = self.storage
        self.storage = import_string("whitenoise.storage.CompressedManifestStaticFilesStorage")()
        yield
        self.storage = self._original_storage
```

Detection of files to be (re-)synchronised:

```python
    def _get_local_manifest(self) -> dict:
        """Open and return local manifest file (json) as dict"""
        with self.static_root.joinpath("staticfiles.json").open() as f:
            return json.load(f)

    def _get_remote_manifest(self) -> dict:
        """Open and return local manifest file (json) as dict"""
        with self.storage.open("staticfiles.json") as f:
            return json.load(f)

    def _detect_differences(self) -> list(str):
        """
        Compares local and remote manifest and returns differences
        """
        local_manifest = self._get_local_manifest()
        remote_manifest = self._get_remote_manifest()
 
        diff_manifest = {
            k: v
            for k, v in local_manifest["paths"].items()
            if remote_manifest.get("paths", {}).get(k, "") != v
        }
        return list(diff_manifest.values())
```

Synchronisation of files:

```python

    def _sync_files_to_s3(self, diff_manifest_files: []):
        """
        Iterates on files collected locally and (re-upload) them if needed
        """
        for file_path in self.static_root.rglob("*"):

            if file_path.is_dir():
                # It's a dir
                # => nothing to do
                continue

            relative_file_path = file_path.relative_to(self.static_root)
            if not any(
                str(relative_file_path).startswith(k) for k in diff_manifest_files
            ):
                # The file already exists remotely and doesn't have changed
                # => nothing to do
                continue

            # The file is new or has changed
            # => upload it
            with Path(file_path).open("rb") as f:
                self.storage.save(str(relative_file_path), f)
```

# To go further

The version described below is deliberately simplified to make it easier to read. A more complete version must :

- support Django's "dry run" option
- offer an option to force global resynchronisation of all files
- remove locally collected temporary static files
- add logs