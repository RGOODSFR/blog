Title: Django : Accélérer la collecte des fichiers statiques sur AWS S3
Date: 2024-02-23 18:00
Id: 0004
Slug: django-accelerer-collectstatic-sur-aws-s3
Lang: fr
Category: développement
Tags: django, aws
Summary: Notre stratégie pour rendre beaucoup plus rapide et plus économe la collecte des fichiers statiques d'une application Django sur AWS S3.

# Le problème

Lorsque l'on stocke les fichiers statiques d'une application Django sur AWS S3, on utilise en général [django-storages](https://pypi.org/project/django-storages/) et [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html).

Dans cette configuration, la collecte des fichiers statiques peut s'avérer [particulièrement lente](https://github.com/jschneier/django-storages/issues/904). La raison est simple : tous les fichiers déjà existants sont téléchargés avant d'être comparés pour savoir si ils doivent être ou non (ré-)uploadés.

[Collectfast](https://pypi.org/project/Collectfast/) propose une solution, mais elle ne fonctionne pas lorsque les noms des fichiers contiennent des hashs, ce qui est le cas lorsque [Whitenoise](https://pypi.org/project/whitenoise/) (par exemple), fait partie de la stack.

Voici comment nous avons améliorer la collecte des fichiers statiques pour la rendre jusqu'à 50x plus rapide dans cette configuration.

# L'approche

L'idée vient de [l'approche proposée ici](https://github.com/jschneier/django-storages/issues/904#issuecomment-1248660983) qui consiste à : 

1. collecter les fichiers statiques en local
2. les synchroniser ensuite sur S3

Les deux inconvénients de cette méthode sont les suivants :

- Il faut supprimer `django-storages` et revenir à un storage backend local classique
- Il faut installer et utiliser la cli AWS pour la synchronisation

Nous avons donc adapté cette approche pour contrer ces inconvénients, en surchargeant la commande `collectstatic` pour qu'elle suive le processus suivant :

1. remplacer temporairement le storage backend par un backend sur système de fichiers local classique comme le `ManifestStaticFilesStorage` de Django ou le `CompressedManifestStaticFilesStorage` de Whitenoise,
2. exécuter le `collectstatic` natif (localement donc),
3. détecter les différences entre les fichiers statiques locaux qui viennent d'être collectés et ceux existants sur S3,
4. uploader les fichiers qui doivent l'être

# La solution

La structure générale :

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

Le context manager :

```python
    @contextmanager
    def _force_file_system_storage(self):
        """
        Replaces S3 static_files storage configured in settings
        by whitenoise (a full-featured local storage with compression and manifest)
        """
        self._original_storage = self.storage
        backend = "whitenoise.storage.CompressedManifestStaticFilesStorage"
        self.storage = import_string(backend)()
        yield
        self.storage = self._original_storage
```

La détection des fichiers à (re-)synchroniser :

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

La synchronisation des fichiers :

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

# Pour aller plus loin

La version décrite ci-dessous est volontairement simplifiée pour la rendre plus lisible. Une version plus complète doit :

- prendre en charge l'option "dry un"`" de Django
- proposer une option permettant de forcer la resynchronisation globale de tous les fichiers
- supprimer les fichiers statiques temporaires collectés localement
- ajouter des logs

Nous avons publiée la [version complète](https://gist.github.com/fle/e21100c5f0d0de9aa62e47da68f99017).