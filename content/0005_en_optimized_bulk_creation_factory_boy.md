Title: Factory-Boy : Optimize bulk creation
Date: 2024-09-12 16:42
Id: 0005
Slug: optimize-bulk-creation-factory_boy
Lang: en
Category: development
Tags: django, tests
Summary: Speed up large dataset creation in factory boy

# The problem

When creating large dataset using [factory_boy](https://pypi.org/project/factory-boy/), you may find yourself using [`MyFactory.create_batch()`](https://factoryboy.readthedocs.io/en/stable/reference.html#factory.create_batch) which is great for specifyng a size, but falls short in terms of performance when using factories based on Django models.

Indeed, here's the related source code:
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

This means that an instance is generated and created for each iteration, resulting in numerous SQL queries, especially if your factory uses `SubFactory` (related model factories).

# The solution

To prevent too much SQL queries, it would be better to use `bulk_create` from the Django manager.

A simple solution can be to generate the instance and then saving them, you can also pass parameters (`notifications_enabled` for example):
```python
class ContactFactory(DjangoModelFactory):
    class Meta:
        model = Contact

# Create a thousand contacts
contact_list = ContactFactory.simple_generate_batch(
    create=False, size=1000, notifications_enabled=True
)
contact_list = Contact.objects.bulk_create(contact_list)
```

But what if our factory has a `SubFactory`? You would certainly hit a N+1 problem. To overcome it, you may bulk create sequentially, while retaining primary keys:

```python
class ContactFactory(DjangoModelFactory):
    class Meta:
        model = Contact

class NotificationFactory(DjangoModelFactory)
    contact = factory.SubFactory(ContactFactory)

    class Meta:
        model = Notification

size = 1000
# Create contacts
contact_list = ContactFactory.simple_generate_batch(
    create=False, size=size, notifications_enabled=True
)
contact_list = Contact.objects.bulk_create(contact_list)

# Create a notification for each contact
obj_list = NotificationFactory.simple_generate_batch(
    create=False, size=size, contact=None
)
for pos, obj in enumerate(obj_list):
    obj.contact_id = contact_list[pos].pk
Notification.objects.bulk_create(obj_list)
```
