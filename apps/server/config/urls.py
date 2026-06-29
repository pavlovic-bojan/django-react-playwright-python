"""URL configuration for the ``config`` project.

The REST API lives under ``/api/``. The built React SPA (when present) is
served same-origin by WhiteNoise at ``/`` — see ``config.settings`` — so there
is no SPA route here; ``/api/*`` requests never match a static file and fall
through to the DRF urls below.
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("todos.urls")),
]
