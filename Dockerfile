# syntax=docker/dockerfile:1
#
# Single image holding the whole Todo app:
#   - apps/client : React build (served same-origin by Django via WhiteNoise)
#   - apps/server : Django + DRF API
#   - apps/tests  : Playwright (Python) E2E/API suite
#
# Running the container executes the full pipeline (see docker/entrypoint.sh):
#   migrate -> seed 10 todos -> serve -> backend unit+integration -> playwright ui+api
#   -> generate Allure report.

# ---------------------------------------------------------------------------
# Stage 1 — build the React client and run its unit/component tests (node)
# ---------------------------------------------------------------------------
FROM node:20-bookworm AS client
WORKDIR /client

COPY apps/client/package*.json ./
RUN npm ci

COPY apps/client/ ./
# Ensure the allure-results dir exists even if no tests emit (keeps COPY below safe).
RUN mkdir -p allure-results
# Client unit + component tests (Vitest). Don't fail the image build on test failures —
# results are carried into the unified Allure report; CI also runs them as a gating job.
RUN npm test || echo "⚠ client tests reported failures (captured in Allure)"
# Production build -> apps/client/dist
RUN npm run build

# ---------------------------------------------------------------------------
# Stage 2 — runtime: Django server + Playwright Python tests + Allure
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive \
    DJANGO_SETTINGS_MODULE=config.settings \
    DEBUG=0 \
    ALLOWED_HOSTS=* \
    ALLURE_RESULTS=/allure-results \
    ALLURE_REPORT=/allure-report \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# System deps: Java (for the Allure CLI), curl/unzip (to fetch Allure), bash.
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl unzip bash default-jre-headless \
    && rm -rf /var/lib/apt/lists/*

# Allure command-line tool.
ARG ALLURE_VERSION=2.30.0
RUN curl -sSL -o /tmp/allure.zip \
      "https://github.com/allure-framework/allure2/releases/download/${ALLURE_VERSION}/allure-${ALLURE_VERSION}.zip" \
    && unzip -q /tmp/allure.zip -d /opt \
    && ln -s "/opt/allure-${ALLURE_VERSION}/bin/allure" /usr/local/bin/allure \
    && rm /tmp/allure.zip

WORKDIR /app

# Python deps for both server and tests (single global env in the image).
COPY apps/server/requirements.txt /app/server-requirements.txt
COPY apps/tests/requirements.txt /app/tests-requirements.txt
RUN pip install -r /app/server-requirements.txt -r /app/tests-requirements.txt

# Playwright browser + its OS dependencies.
RUN playwright install --with-deps chromium

# Application code.
COPY apps/server/ /app/server/
COPY apps/tests/ /app/tests/

# Built SPA -> served by Django/WhiteNoise from apps/server/spa (WHITENOISE_ROOT).
COPY --from=client /client/dist/ /app/server/spa/

# STATIC_ROOT must exist so WhiteNoise doesn't warn at startup (we don't use it for the
# SPA — that's served from spa/ — but Django points STATIC_ROOT here).
RUN mkdir -p /app/server/staticfiles

# Client Allure results staged separately so a runtime volume mount on
# /allure-results doesn't hide them; entrypoint copies them in after the mount.
COPY --from=client /client/allure-results/ /client-allure-results/

# Entrypoint pipeline.
COPY docker/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/app/entrypoint.sh"]
