"""Runtime configuration read from the environment.

The suite must work in two topologies without code changes:

* Local dev   — Vite client on :5173, Django API on :8000. The SPA and API are
  cross-origin, so BASE_URL/API_URL are set explicitly.
* Container   — the built SPA is served same-origin by Django at :8000 and the
  API lives under /api on the same host (no CORS). These defaults match it.
"""
import os

# The UI the browser navigates to. Same-origin SPA root in the image.
BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")

# The REST API root used by both the seeding fixture and the API test cases.
API_URL = os.environ.get("API_URL", "http://localhost:8000/api")
