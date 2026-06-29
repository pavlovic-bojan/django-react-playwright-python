"""Custom DRF exception handler.

Delegates all response generation to DRF's default handler — preserving the
wire format required by the api-contract — while adding structured logging so
every API error and every unhandled exception is recorded with context.
"""

import logging
from typing import Any

from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(
    exc: Exception,
    context: dict[str, Any],
) -> Response | None:
    """Log the exception then delegate to DRF's default exception handler.

    The response shape is unchanged from the DRF default — field-keyed error
    arrays for validation failures, ``"detail"`` for other API errors — so the
    frontend zod schema and E2E tests are unaffected.

    Args:
        exc: The exception raised inside the view.
        context: DRF context dict containing ``"view"``, ``"request"``, etc.

    Returns:
        A ``Response`` for known DRF exceptions, ``None`` for unhandled ones
        (DRF will re-raise the exception in that case).
    """
    response = drf_exception_handler(exc, context)

    view_name = type(context["view"]).__name__ if context.get("view") else "unknown"

    if response is None:
        logger.error(
            "Unhandled exception in view %s: %s",
            view_name,
            exc,
            exc_info=True,
        )
    else:
        logger.warning(
            "API %s in view %s: %s",
            response.status_code,
            view_name,
            exc,
        )

    return response
