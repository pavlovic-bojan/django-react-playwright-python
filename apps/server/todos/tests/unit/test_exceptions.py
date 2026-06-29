"""Unit tests for the custom DRF exception handler.

The handler must:
1. Delegate response generation to DRF's default handler (preserving the
   api-contract wire format).
2. Return a ``Response`` for known DRF exceptions.
3. Return ``None`` for unhandled exceptions (DRF re-raises in that case).
4. Log in both cases without raising.
"""

import logging

import allure
import pytest
from rest_framework.exceptions import NotFound, ValidationError

from todos.exceptions import custom_exception_handler


@allure.feature("Todos API")
@allure.story("Exception handler")
@pytest.mark.unit
class TestCustomExceptionHandler:
    """Custom DRF exception handler returns correct responses and logs."""

    def test_validation_error_returns_400_response(self) -> None:
        exc = ValidationError({"title": ["This field may not be blank."]})
        context: dict = {"view": None}
        response = custom_exception_handler(exc, context)
        assert response is not None
        assert response.status_code == 400

    def test_not_found_returns_404_response(self) -> None:
        exc = NotFound()
        context: dict = {"view": None}
        response = custom_exception_handler(exc, context)
        assert response is not None
        assert response.status_code == 404

    def test_unhandled_exception_returns_none(self) -> None:
        exc = RuntimeError("something unexpected")
        context: dict = {"view": None}
        response = custom_exception_handler(exc, context)
        assert response is None

    def test_handled_exception_logs_warning(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        exc = ValidationError({"title": ["blank"]})
        context: dict = {"view": None}
        with caplog.at_level(logging.WARNING, logger="todos.exceptions"):
            custom_exception_handler(exc, context)
        assert "400" in caplog.text

    def test_unhandled_exception_logs_error(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        exc = ValueError("boom")
        context: dict = {"view": None}
        with caplog.at_level(logging.ERROR, logger="todos.exceptions"):
            custom_exception_handler(exc, context)
        assert "boom" in caplog.text

    def test_context_with_view_name_logged(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """When view is present, its class name appears in the log output."""

        class FakeView:
            pass

        exc = NotFound()
        context: dict = {"view": FakeView()}
        with caplog.at_level(logging.WARNING, logger="todos.exceptions"):
            custom_exception_handler(exc, context)
        assert "FakeView" in caplog.text
