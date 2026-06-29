# Build the single image and run the full pipeline locally (Windows / PowerShell).
#
#   .\run-local.ps1
#
# Requires Docker Desktop. Produces .\allure-results and .\allure-report on the host.

$ErrorActionPreference = "Stop"

New-Item -ItemType Directory -Force -Path .\allure-results | Out-Null
New-Item -ItemType Directory -Force -Path .\allure-report  | Out-Null

Write-Host "==> Building image and running the pipeline (migrate -> seed -> tests -> allure)..." -ForegroundColor Cyan
# --abort-on-container-exit so compose returns when the pipeline finishes.
docker compose up --build --abort-on-container-exit
$pipelineExit = $LASTEXITCODE

docker compose down --remove-orphans | Out-Null

Write-Host ""
Write-Host "==> Pipeline finished (exit $pipelineExit)." -ForegroundColor Cyan
Write-Host "    Allure report written to .\allure-report"
Write-Host ""
Write-Host "    View it with either:"
Write-Host "      allure open .\allure-report                 # if the Allure CLI is installed"
Write-Host "      cd allure-report; python -m http.server 8800  # then open http://localhost:8800"

exit $pipelineExit
