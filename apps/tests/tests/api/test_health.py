"""Health endpoint contract test.

GET /api/health/ must return 200 with {"status": "ok"}.
Used as a liveness probe by the container entrypoint.
"""
import allure
import jsonschema
import pytest

from schemas.todo_schemas import HEALTH_SCHEMA


@allure.feature("API")
@allure.story("Health")
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.api
@allure.title("GET /api/health/ returns 200 with {{status: ok}} matching the schema")
def test_health_endpoint_returns_200_and_ok(api_context):
    with allure.step("GET /api/health/"):
        res = api_context.get("health/")

    with allure.step("Status code is 200"):
        assert res.status == 200, res.text()

    with allure.step("Body matches the health schema"):
        body = res.json()
        jsonschema.validate(instance=body, schema=HEALTH_SCHEMA)

    with allure.step("status field equals 'ok'"):
        assert body["status"] == "ok"
