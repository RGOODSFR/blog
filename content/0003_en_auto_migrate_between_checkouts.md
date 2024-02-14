Title: Django: automatically migrate between git checkouts
Date: 2024-02-14 14:00
Id: 0003
Slug: auto-migrate-between-checkouts
Lang: en
Category: django
Status: draft
Summary: How to use git hooks to automatically reset your database state to one compatible ith branches you are checking.

# The problem

When working in a team and peer-reviewing code, you might find yourself navigating between branches a lot, 
and with the way Django manages database state through migrations, you can easily forget to unaply migrations before changing branches.
Let's see how we can improve that.

# Detecting differences in migrations

The right moment for checking migrations state is when code changes by inovoking a `git checkout`, so we can make use 
of [git hooks](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks) for that.

Now, in this hooks, we must be aware of the django setup (settings, database, and so on), so we'll be working 
through a [management command](https://docs.djangoproject.com/en/5.0/howto/custom-management-commands/) to easily have the Django context.

To check for difference in migrations, I initially looked into the `--prune` option of [`migrate`](https://github.com/django/django/blob/5.0/django/core/management/commands/migrate.py#L191-240) command 
as it detects the difference between applied migrations (existing in database) and those declared in code.

This part is using the migrations loader to check for applied missing migrations and delete them:
```python
set(executor.loader.applied_migrations) - set(executor.loader.disk_migrations)
```

We can use this bit to just check for applied missing migrations, and warn the user about them:
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

Note that along with the warning, we also output which command to execute to revert the database to a common state (between database state and file state),
it will be useful in our git hook.

# Automatically revert migrations upon checkout

Now that we can detect differences, let's go a step further and actually migrate upon checkout of branches. This can be done through a bash script that will use as a git hook:
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

- `GIT_CHECKOUTING` is an environment variable we set to prevent recursive calls
- we use `git checkout -` to return to the previous branch and migrate to the common state, then run it again to come back to checkouted branch

# Some limitations

This works only if 
 - your migrations have reverse operations
 - your database state is not broken
 - you set the right directory `src` in this git hook
