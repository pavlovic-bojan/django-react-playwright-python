from django.db import models


class Todo(models.Model):
    """A single todo item.

    Server-managed timestamps use ``auto_now_add`` / ``auto_now``; the default
    ordering is newest-first to match the API contract's list endpoint.
    """

    title = models.CharField(max_length=255)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self) -> str:
        return self.title
