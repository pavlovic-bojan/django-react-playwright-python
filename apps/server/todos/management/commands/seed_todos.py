"""Management command: seed_todos

Populates the database with sample todo items.  Designed to be idempotent —
any existing todos are deleted before the new ones are created.

Usage::

    python manage.py seed_todos            # create 10 todos (default)
    python manage.py seed_todos --count 3  # create exactly 3 todos
"""

from argparse import ArgumentParser

from django.core.management.base import BaseCommand

from todos.models import Todo

DEFAULT_COUNT = 10


class Command(BaseCommand):
    help = "Seed the database with sample todos (clears existing todos first)."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "--count",
            type=int,
            default=DEFAULT_COUNT,
            help=f"Number of todos to create (default: {DEFAULT_COUNT}).",
        )

    def handle(self, *args: object, **options: object) -> None:
        count: int = options["count"]  # type: ignore[assignment]
        if count < 0:
            self.stderr.write("--count must be >= 0")
            return

        # Clear existing todos so the command is idempotent.
        deleted, _ = Todo.objects.all().delete()

        todos = [
            Todo(title=f"Sample todo #{i}", completed=(i % 3 == 0))
            for i in range(1, count + 1)
        ]
        Todo.objects.bulk_create(todos)

        self.stdout.write(
            self.style.SUCCESS(
                f"Cleared {deleted} existing row(s); created {count} todo(s)."
            )
        )
