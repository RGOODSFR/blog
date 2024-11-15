Title: Factory-Boy : Optimiser la création en masse
Date: 2024-09-12 16:42
Id: 0005
Slug: optimiser-creation-en-masse-factory_boy
Lang: fr
Category: développement
Tags: django, tests
Summary: Accélérer la création de grands ensembles de données avec factory_boy


# Le problème

Lorsque vous créez de grands ensembles de données en utilisant [factory_boy](https://pypi.org/project/factory-boy/), vous pouvez vous retrouver à utiliser [`MyFactory.create_batch()`](https://factoryboy.readthedocs.io/en/stable/reference.html#factory.create_batch), ce qui est excellent pour spécifier la taille de la liste, mais est limité en termes de performance lorsqu'il s'agit de factory basées sur des modèles Django.

En effet, voici le code source concerné :

```python
    @classmethod
    def create_batch(cls, size, **kwargs):
        """Create a batch of instances of the given class, with overridden attrs.

        Args:
            size (int): the number of instances to create

        Returns:
            object list: the created instances
        """
        return [cls.create(**kwargs) for _ in range(size)]
```

Cela signifie qu'une instance est générée et créée pour chaque itération, entraînant de nombreuses requêtes SQL, surtout si votre factory utilise `SubFactory` (lorsqu'un modèle est associé via une `ForeignKey`).

# La solution

Pour éviter trop de requêtes SQL, il serait préférable d'utiliser `bulk_create` depuis le manager Django.

Une solution simple consiste à générer les instances puis à les sauvegarder. Vous pouvez également passer des paramètres (comme `notifications_enabled` par exemple) :

```python
class ContactFactory(DjangoModelFactory):
    class Meta:
        model = Contact

# Créer mille contacts
contact_list = ContactFactory.simple_generate_batch(
    create=False, size=1000, notifications_enabled=True
)
contact_list = Contact.objects.bulk_create(contact_list)
```

Mais que faire si notre factory a une `SubFactory` ? Vous rencontrerez certainement un problème de N+1. Pour y remédier, vous pouvez créer en masse séquentiellement, en conservant les clés primaires :


```python
class ContactFactory(DjangoModelFactory):
    class Meta:
        model = Contact

class NotificationFactory(DjangoModelFactory)
    contact = factory.SubFactory(ContactFactory)

    class Meta:
        model = Notification

size = 1000
# Création des contacts
contact_list = ContactFactory.simple_generate_batch(
    create=False, size=size, notifications_enabled=True
)
contact_list = Contact.objects.bulk_create(contact_list)

# Créer une notification pour chaque contact
obj_list = NotificationFactory.simple_generate_batch(
    create=False, size=size, contact=None
)
for pos, obj in enumerate(obj_list):
    obj.contact_id = contact_list[pos].pk
Notification.objects.bulk_create(obj_list)
```
