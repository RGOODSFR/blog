Title: Django: migrer automatiquement entre les checkouts git
Date: 2024-02-14 14:00
Id: 0003
Slug: django-migrer-automatiquement-entre-checkouts-git
Lang: fr
Category: django
Summary: Comment utiliser les hooks git pour réinitialiser automatiquement l'état de votre base de données à un état compatible avec la branche sur laquelle vous basculez.

# Le problème

Lorsque l'on travaille en équipe et que l'on relit le code, il arrive souvent que l'on navigue entre les branches, 
et avec la façon dont Django gère l'état de la base de données et son système de migrations, vous pouvez facilement oublier de désappliquer les migrations avant de changer de branche. 
Voyons comment nous pouvons améliorer cela.

# Détection des différences dans les migrations

Le bon moment pour vérifier l'état des migrations est lorsque le code change en lançant un `git checkout`, nous pouvons donc utiliser les [hooks de git](https://git-scm.com/book/fr/v2/Personnalisation-de-Git-Crochets-Git) pour cela.

Maintenant, dans ce hook, nous devons avoir le contexte de configuration de django (paramètres, base de données, et ainsi de suite), donc nous allons travailler avec une [commande personnalisée](https://docs.djangoproject.com/fr/5.0/howto/custom-management-commands/) pour avoir facilement le contexte de Django.

Pour vérifier les différences dans les migrations, j'ai d'abord regardé l'option `--prune` de la commande [`migrate`](https://github.com/django/django/blob/5.0/django/core/management/commands/migrate.py#L191-240) 
car elle détecte la différence entre les migrations appliquées (existant dans la base de données) et celles déclarées dans le code.

Cette partie utilise le `MigrationExecutor` pour vérifier les migrations manquantes appliquées et les supprimer :
``python
set(executor.loader.applied_migrations) - set(executor.loader.disk_migrations)
```

Nous pouvons utiliser ce bout de code pour simplement vérifier les migrations manquantes appliquées, et avertir l'utilisateur à ce sujet :
```python
from collections import defaultdict

from django.core.management import BaseCommand
from django.db import connection
from django.db.migrations.executor import MigrationExecutor


class Command(BaseCommand):
    def handle(self, *args, **options):
        executor = MigrationExecutor(connection)
        applied_missing_migrations = set(executor.loader.applied_migrations) - set(
            executor.loader.disk_migrations
        )
        if applied_missing_migrations:
            self.stderr.write(
                "Warning: you have applied migrations that no longer exist:"
            )
            for app_label, migration_name in applied_missing_migrations:
                self.stderr.write(
                    f" - {app_label}: {migration_name}", style_func=self.style.WARNING
                )

            # Determine which migration number to revert to
            revert_commands = defaultdict(lambda: "9999")
            for app_label, migration_name in applied_missing_migrations:
                [migration_number, *_] = migration_name.split("_")
                if int(migration_number) - 1 < int(revert_commands[app_label]):
                    revert_commands[app_label] = (
                        "zero"
                        if int(migration_number) - 1 == 0
                        else f"{int(migration_number) - 1:0>4}"
                    )

            # Write the result to stdout for further use
            for app_label, migration_number in revert_commands.items():
                self.stdout.write(f"./manage.py migrate {app_label} {migration_number}")
```

Notez qu'en plus de l'avertissement, nous retournons également la commande à exécuter dans la sortie standard pour ramener la base de données à un état commun (entre l'état de la base de données et l'état du fichier), cela sera utile dans notre hook git.

# Revenir automatiquement sur les migrations lors du checkout

Maintenant que nous pouvons détecter les différences, allons un peu plus loin et effectuons les migrations lors du checkout des branches. Cela peut être fait via un script bash qui sera utilisé pour le hook git :
```bash
#!/bin/bash
if [ "$3" -eq 1 ] && [ -z ${GIT_CHECKOUTING+x} ]
then
  export GIT_CHECKOUTING=1
  # Get our commands to execute
  result=$(python src/manage.py check_applied_missing_migrations 2> /dev/null)
  if [ -n "$result" ]
  then
    echo "Migrations must be reverted:"
    echo ""
    echo "$result"
    git checkout - > /dev/null
    (cd src && eval "$result")
    git checkout - > /dev/null
    (cd src && ./manage.py migrate)
  fi
  unset GIT_CHECKOUTING
fi
```

- `GIT_CHECKOUTING` est une variable d'environnement que nous définissons pour éviter les appels récursifs
- on utilise `git checkout -` pour revenir à la branche précédente et migrer vers l'état commun, puis pour revenir à la branche orignalement demandée

# Quelques limitations

Cela ne fonctionne que si :
 - vos migrations ont des opérations inverses (paramètre `reverse`)
 - l'état de votre base de données est sain
 - le répertoire de travail `src` dans ce hook git est adapté à votre projet