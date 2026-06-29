import allure
import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture(autouse=True)
def _allure_category(request: pytest.FixtureRequest) -> None:
    """Group each test under a top-level Allure category by its directory.

    Drives both the "Suites" tab (parentSuite) and the "Behaviors" tab (epic) so a
    first-time reader sees "Django unit tests" and "Django integration tests" rather
    than a flat list.
    """
    path = str(request.node.fspath).replace("\\", "/")
    if "/tests/unit/" in path:
        category = "Django unit tests"
    elif "/tests/integration/" in path:
        category = "Django integration tests"
    else:
        return
    allure.dynamic.parent_suite(category)
    allure.dynamic.epic(category)
