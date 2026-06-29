"""Serializers — the DTO layer for the todos domain.

A DRF serializer plays the same role as a DTO in Spring Boot / NestJS:
it defines the wire shape, owns validation, and decouples the client format
from the DB model.  Read and write shapes are currently identical (see the
api-contract skill), so a single serializer suffices.

Validation strategy for ``title``:
- ``trim_whitespace=False`` disables DRF's built-in strip so that our
  ``validate_title`` is the single, explicit place where trimming and
  the blank guard both live.  This keeps the validation rule visible and
  fully testable without relying on implicit DRF field behaviour.
"""

from rest_framework import serializers

from .models import Todo


class TodoSerializer(serializers.ModelSerializer):
    """DTO for the Todo resource.

    ``id`` / ``created_at`` / ``updated_at`` are server-managed and
    therefore declared ``read_only``.  The client may supply ``title``
    and ``completed``; all other fields on write paths are ignored.
    """

    class Meta:
        model = Todo
        fields = ["id", "title", "completed", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
        # Disable DRF's silent whitespace strip so validate_title owns it.
        extra_kwargs = {"title": {"trim_whitespace": False}}

    def validate_title(self, value: str) -> str:
        """Trim whitespace and reject a blank or whitespace-only title."""
        value = value.strip()
        if not value:
            raise serializers.ValidationError("This field may not be blank.")
        return value
