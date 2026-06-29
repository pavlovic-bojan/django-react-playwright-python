import allure
import pytest

from todos.models import Todo


@allure.feature("Todos API")
@allure.story("Model")
@pytest.mark.unit
class TestTodoModel:
    def test_str_returns_title(self):
        todo = Todo(title="Buy milk")
        assert str(todo) == "Buy milk"

    def test_completed_defaults_to_false(self):
        # Field default is declared on the model, independent of the DB.
        assert Todo._meta.get_field("completed").default is False

    def test_default_ordering_is_newest_first(self):
        assert Todo._meta.ordering == ["-created_at", "-id"]

    @pytest.mark.django_db
    def test_ordering_newest_first_from_db(self):
        first = Todo.objects.create(title="first")
        second = Todo.objects.create(title="second")
        third = Todo.objects.create(title="third")

        ids = list(Todo.objects.values_list("id", flat=True))
        assert ids == [third.id, second.id, first.id]

    @pytest.mark.django_db
    def test_timestamps_are_set_on_create(self):
        todo = Todo.objects.create(title="with timestamps")
        assert todo.created_at is not None
        assert todo.updated_at is not None
