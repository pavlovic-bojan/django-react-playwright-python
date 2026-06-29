#!/usr/bin/env bash
#
# Full in-container pipeline:
#   migrate -> seed 10 todos -> serve -> backend unit+integration tests
#   -> playwright ui+api tests -> generate Allure report.
#
# Test results from all suites land in $ALLURE_RESULTS and are combined into one
# Allure report at $ALLURE_REPORT. The container exit code reflects the backend +
# Playwright (Python) test outcome.

set -u

ALLURE_RESULTS="${ALLURE_RESULTS:-/allure-results}"
ALLURE_REPORT="${ALLURE_REPORT:-/allure-report}"
mkdir -p "$ALLURE_RESULTS" "$ALLURE_REPORT"

# Bring in the client (Vitest) Allure results staged at build time. Done here, after
# any runtime volume mount on /allure-results, so they are not hidden by the mount.
if [ -d /client-allure-results ]; then
  cp -r /client-allure-results/. "$ALLURE_RESULTS"/ 2>/dev/null || true
fi

echo "==> [1/6] Migrate database (SQLite)"
cd /app/server
python manage.py migrate --noinput

echo "==> [2/6] Seed 10 demo todos"
python manage.py seed_todos --count 10

echo "==> [3/6] Start Django (gunicorn) on :8000"
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 60 &
SERVER_PID=$!

echo "==> Waiting for the server to become healthy..."
healthy=0
for _ in $(seq 1 30); do
  if curl -sf http://localhost:8000/api/health/ >/dev/null 2>&1; then
    healthy=1
    echo "    server is healthy"
    break
  fi
  sleep 1
done
if [ "$healthy" -ne 1 ]; then
  echo "!! server did not become healthy in time" >&2
  kill "$SERVER_PID" 2>/dev/null || true
  exit 1
fi

rc=0

echo "==> [4/6] Backend unit + integration tests (pytest-django)"
cd /app/server
pytest -q --alluredir="$ALLURE_RESULTS" || rc=1

echo "==> [5/6] Playwright UI + API tests (pytest-playwright)"
cd /app/tests
# Disable pytest-django for the Playwright suite (it lives outside the Django project).
unset DJANGO_SETTINGS_MODULE
BASE_URL="http://localhost:8000" \
API_URL="http://localhost:8000/api" \
  pytest -q -p no:django --alluredir="$ALLURE_RESULTS" || rc=1

echo "==> Normalising Allure suite labels (one parentSuite per test)"
# allure-vitest adds a second parentSuite (the describe block name) on top of the
# category we set, which scrambles the "Suites" tab. Keep a single parentSuite equal
# to the test's category (its epic) and demote the framework's auto value to a suite.
python - "$ALLURE_RESULTS" <<'PYEOF' || echo "!! label normalisation skipped"
import glob, json, os, sys

results_dir = sys.argv[1]
for path in glob.glob(os.path.join(results_dir, "*-result.json")):
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (ValueError, OSError):
        continue
    labels = data.get("labels", [])
    epics = [l["value"] for l in labels if l.get("name") == "epic"]
    if not epics:
        continue
    category = epics[0]
    extras = [
        l["value"]
        for l in labels
        if l.get("name") == "parentSuite" and l.get("value") != category
    ]
    labels = [l for l in labels if l.get("name") != "parentSuite"]
    labels.append({"name": "parentSuite", "value": category})
    if extras and not any(l.get("name") == "suite" for l in labels):
        labels.append({"name": "suite", "value": extras[0]})
    data["labels"] = labels
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh)
PYEOF

echo "==> [6/6] Generate Allure report"
allure generate "$ALLURE_RESULTS" -o "$ALLURE_REPORT" --clean || \
  echo "!! allure report generation failed (results still available)"

kill "$SERVER_PID" 2>/dev/null || true

echo "==> Done (test exit code: $rc)"
echo "    Allure results: $ALLURE_RESULTS"
echo "    Allure report:  $ALLURE_REPORT (open index.html)"
exit "$rc"
