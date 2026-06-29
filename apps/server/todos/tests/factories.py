"""factory_boy factories for test data.

Use these in tests instead of ``Todo.objects.create(...)`` so that object
construction logic is centralised and tests only specify the fields they care
about.

Example::

    todo = TodoFactory()                    # auto title, completed=False
    done = TodoFactory(completed=True)      # specific field
    batch = TodoFactory.create_batch(5)     # 5 todos at once
"""

import factory

from todos.models import Todo


class TodoFactory(factory.django.DjangoModelFactory):
    """Factory for :class:`todos.models.Todo`."""

    class Meta:
        model = Todo

    # Sequence ensures each factory-created todo has a unique, readable title.
    title = factory.Sequence(lambda n: f"Test todo #{n}")
    completed = False
