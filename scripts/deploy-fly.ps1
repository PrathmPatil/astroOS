# Deploy AstroOS to Fly.io (Windows)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

$flyBin = "$env:USERPROFILE\.fly\bin"
$env:Path = "$flyBin;$env:Path"
$fly = Join-Path $flyBin "flyctl.exe"

if (-not (Test-Path $fly)) {
  Write-Host "Installing flyctl..."
  iwr https://fly.io/install.ps1 -useb | iex
}

Write-Host "==> Auth check"
& $fly auth whoami

Write-Host "==> Ensure apps exist (ignore errors if already created)"
& $fly apps create astroos-api 2>$null
& $fly apps create astroos-web 2>$null

Write-Host "==> Deploy API"
& $fly deploy --config fly.api.toml

Write-Host "==> Deploy Web"
& $fly deploy --config fly.web.toml

Write-Host ""
Write-Host "API: https://astroos-api.fly.dev/docs"
Write-Host "Web: https://astroos-web.fly.dev"
Write-Host "Done."
