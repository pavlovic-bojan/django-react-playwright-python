"""Unit tests for settings-level helpers.

These tests exercise ``_env_bool`` — the private helper that converts
environment-variable strings to Python booleans.  It is imported directly
from ``config.settings`` (it is module-level, therefore importable).

The SPA-directory block in settings.py is intentionally excluded from
coverage (``# pragma: no cover``) because it depends on deployment-time
filesystem state that is not reproducible in a unit-test context.
"""

import pytest

from config.settings import _env_bool


@pytest.mark.unit
class TestEnvBool:
    """Tests for the _env_bool environment-variable helper."""

    def test_returns_true_default_when_var_absent(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("_TEST_BOOL_VAR", raising=False)
        assert _env_bool("_TEST_BOOL_VAR", True) is True

    def test_returns_false_default_when_var_absent(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("_TEST_BOOL_VAR", raising=False)
        assert _env_bool("_TEST_BOOL_VAR", False) is False

    @pytest.mark.parametrize(
        "raw", ["1", "true", "yes", "on", "TRUE", "YES", "ON", "True"]
    )
    def test_truthy_strings_return_true(
        self, monkeypatch: pytest.MonkeyPatch, raw: str
    ) -> None:
        monkeypatch.setenv("_TEST_BOOL_VAR", raw)
        assert _env_bool("_TEST_BOOL_VAR", False) is True

    @pytest.mark.parametrize(
        "raw", ["0", "false", "no", "off", "False", "NO", "anything"]
    )
    def test_falsy_strings_return_false(
        self, monkeypatch: pytest.MonkeyPatch, raw: str
    ) -> None:
        monkeypatch.setenv("_TEST_BOOL_VAR", raw)
        assert _env_bool("_TEST_BOOL_VAR", True) is False
