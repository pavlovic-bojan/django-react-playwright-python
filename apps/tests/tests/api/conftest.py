"""API-test-local fixtures.

``api_cleanup`` records todo ids created through the Playwright APIRequestContext
and deletes them on teardown, keeping API tests isolated from each other and from
the seeded demo data.
"""
import pytest


@pytest.fixture
def api_cleanup(api_context):
    created: list[int] = []
    yield created
    for todo_id in created:
        api_context.delete(f"todos/{todo_id}/")
