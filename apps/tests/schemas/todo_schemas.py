"""JSON Schema definitions — single source of truth for API response validation.

These schemas mirror the api-contract skill exactly. Every API test validates
its response body with ``jsonschema.validate(body, SCHEMA)`` so that shape
regressions are caught immediately.

Sync rule: when the api-contract changes, update this file first, then the
DRF serializer and the zod schema.
"""

# ---------------------------------------------------------------------------
# Todo object — the 5 contract fields, strict (additionalProperties: False).
# ---------------------------------------------------------------------------
TODO_SCHEMA: dict = {
    "type": "object",
    "required": ["id", "title", "completed", "created_at", "updated_at"],
    "properties": {
        "id": {"type": "integer"},
        "title": {"type": "string", "minLength": 1, "maxLength": 255},
        "completed": {"type": "boolean"},
        "created_at": {"type": "string"},  # ISO-8601; format validated by API
        "updated_at": {"type": "string"},  # ISO-8601; format validated by API
    },
    "additionalProperties": False,
}

# ---------------------------------------------------------------------------
# List endpoint — plain array, no pagination wrapper.
# ---------------------------------------------------------------------------
TODO_LIST_SCHEMA: dict = {
    "type": "array",
    "items": TODO_SCHEMA,
}

# ---------------------------------------------------------------------------
# Health probe — GET /api/health/ → {"status": "ok"}
# ---------------------------------------------------------------------------
HEALTH_SCHEMA: dict = {
    "type": "object",
    "required": ["status"],
    "properties": {
        "status": {"type": "string", "enum": ["ok"]},
    },
    "additionalProperties": False,
}

# ---------------------------------------------------------------------------
# 400 validation error — DRF default shape: field-keyed arrays of strings.
# Example: {"title": ["This field may not be blank."]}
# ---------------------------------------------------------------------------
ERROR_400_SCHEMA: dict = {
    "type": "object",
    "minProperties": 1,
    "additionalProperties": {
        "type": "array",
        "items": {"type": "string"},
        "minItems": 1,
    },
}

# ---------------------------------------------------------------------------
# 404 not-found error — DRF default: {"detail": "Not found."}
# ---------------------------------------------------------------------------
ERROR_404_SCHEMA: dict = {
    "type": "object",
    "required": ["detail"],
    "properties": {
        "detail": {"type": "string"},
    },
}
