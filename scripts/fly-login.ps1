# Opens an interactive Fly.io login in a new Windows Terminal / PowerShell window.
# Cursor cannot complete browser login for you — run this once on your PC.

$fly = Join-Path $env:USERPROFILE ".fly\bin\flyctl.exe"
if (-not (Test-Path $fly)) {
  Write-Host "Installing flyctl..."
  iwr https://fly.io/install.ps1 -useb | iex
  $fly = Join-Path $env:USERPROFILE ".fly\bin\flyctl.exe"
}

Write-Host ""
Write-Host "A new window will open. In THAT window:"
Write-Host "  1. Browser opens for Fly.io"
Write-Host "  2. Sign up / log in"
Write-Host "  3. Approve the CLI"
Write-Host "  4. Wait until it says you are logged in"
Write-Host ""
Write-Host "Then come back here and run: .\scripts\deploy-fly.ps1"
Write-Host ""

$cmd = @"
`$env:Path = '$env:USERPROFILE\.fly\bin;' + `$env:Path
& '$fly' auth login
Write-Host ''
Write-Host 'Login finished. Checking...'
& '$fly' auth whoami
Write-Host ''
Write-Host 'Press any key to close...'
`$null = `$Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $cmd
Write-Host "Login window launched."
