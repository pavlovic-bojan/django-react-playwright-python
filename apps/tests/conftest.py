"""Shared fixtures for the Todo E2E suite.

Provides:
* ``base_url``           — overrides pytest-playwright's base_url from BASE_URL env.
* ``api``               — requests-based client for FAST data seeding in UI tests;
                          tracks created todos and deletes them in teardown so every
                          test owns its data (isolation against the seeded demo set).
* ``api_context``       — Playwright APIRequestContext bound to API_URL, used by the
                          API test cases to assert status codes + JSON bodies.
* ``todo_page``         — a TodoPage Page Object already navigated to "/".
* ``unique_suffix``     — per-test unique token so titles never collide with the
                          ~10 seeded demo todos or with other tests.
"""

import os
import sys
import uuid

import allure
import pytest
import requests

# Make ``pages`` and ``config`` importable regardless of pytest's rootdir.
sys.path.insert(0, os.path.dirname(__file__))

from config import API_URL, BASE_URL  # noqa: E402


@pytest.fixture(autouse=True)
def _allure_category(request: pytest.FixtureRequest) -> None:
    """Group each test under a top-level Allure category by its directory.

    Drives both the "Suites" tab (parentSuite) and the "Behaviors" tab (epic) so a
    first-time reader sees "QA UI e2e tests" and "QA API tests" rather than a flat list.
    """
    path = str(request.node.fspath).replace("\\", "/")
    if "/tests/ui/" in path:
        category = "QA UI e2e tests"
    elif "/tests/api/" in path:
        category = "QA API tests"
    else:
        return
    allure.dynamic.parent_suite(category)
    allure.dynamic.epic(category)


@pytest.fixture(scope="session")
def base_url() -> str:
    """Override pytest-base-url's fixture so navigation honours BASE_URL env."""
    return BASE_URL


@pytest.fixture
def unique_suffix() -> str:
    """Short unique token to keep test data distinct from seed + sibling tests."""
    return uuid.uuid4().hex[:8]


class _ApiClient:
    """Thin requests-based helper for seeding/cleaning todos in UI tests."""

    def __init__(self, base: str):
        self.base = base.rstrip("/")
        self.session = requests.Session()
        self._created: list[int] = []

    def create_todo(self, title: str, completed: bool = False) -> dict:
        res = self.session.post(
            f"{self.base}/todos/",
            json={"title": title, "completed": completed},
            timeout=10,
        )
        res.raise_for_status()
        todo = res.json()
        self._created.append(todo["id"])
        return todo

    def cleanup(self) -> None:
        for todo_id in self._created:
            try:
                self.session.delete(f"{self.base}/todos/{todo_id}/", timeout=10)
            except requests.RequestException:
                pass
        self._created.clear()
        self.session.close()


@pytest.fixture
def api():
    """Requests-based seeding client. Deletes everything it created on teardown."""
    client = _ApiClient(API_URL)
    yield client
    client.cleanup()


@pytest.fixture
def api_context(playwright):
    """Playwright APIRequestContext for direct REST contract testing.

    Best-practice Playwright API testing: a real request context with the API
    root as base_url, so test cases assert on HTTP status + JSON bodies.
    """
    context = playwright.request.new_context(
        base_url=API_URL.rstrip("/") + "/",
        extra_http_headers={"Content-Type": "application/json"},
    )
    yield context
    context.dispose()


@pytest.fixture
def todo_page(page):
    """A TodoPage Page Object already navigated to the SPA root."""
    from pages.todo_page import TodoPage

    tp = TodoPage(page)
    tp.goto()
    return tp
