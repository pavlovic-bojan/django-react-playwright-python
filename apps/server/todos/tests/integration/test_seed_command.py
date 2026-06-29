from io import StringIO

import allure
import pytest
from django.core.management import call_command

from todos.models import Todo

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


@allure.feature("Todos API")
@allure.story("Seed command")
def test_seed_default_count():
    call_command("seed_todos")
    assert Todo.objects.count() == 10


@allure.feature("Todos API")
@allure.story("Seed command")
def test_seed_custom_count():
    call_command("seed_todos", "--count", "3")
    assert Todo.objects.count() == 3


@allure.feature("Todos API")
@allure.story("Seed command")
def test_seed_is_idempotent():
    Todo.objects.create(title="stale")
    call_command("seed_todos", "--count", "5")
    # Existing rows cleared first, then exactly 5 created.
    assert Todo.objects.count() == 5


@allure.feature("Todos API")
@allure.story("Seed command")
def test_seed_negative_count_writes_error_and_creates_nothing():
    """--count < 0 must write an error message and leave the DB untouched."""
    stderr = StringIO()
    call_command("seed_todos", "--count", "-1", stderr=stderr)
    assert "--count must be >= 0" in stderr.getvalue()
    assert Todo.objects.count() == 0
