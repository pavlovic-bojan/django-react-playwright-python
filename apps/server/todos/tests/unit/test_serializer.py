import allure
import pytest

from todos.serializers import TodoSerializer


@allure.feature("Todos API")
@allure.story("Serializer / DTO validation")
@pytest.mark.unit
class TestTodoSerializer:
    def test_valid_payload(self):
        serializer = TodoSerializer(data={"title": "Buy milk", "completed": True})
        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data["title"] == "Buy milk"
        assert serializer.validated_data["completed"] is True

    def test_completed_defaults_to_false_when_omitted(self):
        serializer = TodoSerializer(data={"title": "Buy milk"})
        assert serializer.is_valid(), serializer.errors
        # Model default applies; serializer does not require it.
        assert serializer.validated_data.get("completed", False) is False

    def test_blank_title_rejected(self):
        serializer = TodoSerializer(data={"title": ""})
        assert not serializer.is_valid()
        assert "title" in serializer.errors

    def test_whitespace_only_title_rejected(self):
        serializer = TodoSerializer(data={"title": "   "})
        assert not serializer.is_valid()
        assert "title" in serializer.errors
        assert serializer.errors["title"][0] == "This field may not be blank."

    def test_title_is_trimmed(self):
        serializer = TodoSerializer(data={"title": "  Walk dog  "})
        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data["title"] == "Walk dog"

    def test_title_max_length_enforced(self):
        serializer = TodoSerializer(data={"title": "x" * 256})
        assert not serializer.is_valid()
        assert "title" in serializer.errors

    def test_title_max_length_boundary_ok(self):
        serializer = TodoSerializer(data={"title": "x" * 255})
        assert serializer.is_valid(), serializer.errors

    def test_unknown_fields_ignored(self):
        serializer = TodoSerializer(data={"title": "ok", "bogus": "nope"})
        assert serializer.is_valid(), serializer.errors
        assert "bogus" not in serializer.validated_data

    def test_read_only_fields_declared(self):
        fields = TodoSerializer().fields
        for name in ("id", "created_at", "updated_at"):
            assert fields[name].read_only is True
