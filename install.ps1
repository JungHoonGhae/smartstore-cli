$ErrorActionPreference = "Stop"

$repo = "JungHoonGhae/smartstore-cli"
$asset = "storectl-windows-amd64.zip"
$installDir = "$env:LOCALAPPDATA\storectl"

Write-Host "Downloading $asset..."
$url = "https://github.com/$repo/releases/latest/download/$asset"
$tmp = New-TemporaryFile | Rename-Item -NewName { $_.Name + ".zip" } -PassThru

Invoke-WebRequest -Uri $url -OutFile $tmp.FullName

Write-Host "Extracting..."
$extractDir = Join-Path $env:TEMP "storectl-install"
if (Test-Path $extractDir) { Remove-Item $extractDir -Recurse -Force }
Expand-Archive $tmp.FullName -DestinationPath $extractDir

Write-Host "Installing to $installDir..."
if (-not (Test-Path $installDir)) { New-Item -ItemType Directory -Path $installDir | Out-Null }
Copy-Item "$extractDir\storectl.exe" "$installDir\storectl.exe" -Force
if (Test-Path "$extractDir\auth-helper") {
    Copy-Item "$extractDir\auth-helper" "$installDir\auth-helper" -Recurse -Force
}

# Add to PATH if not already there
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($userPath -notlike "*$installDir*") {
    [Environment]::SetEnvironmentVariable("Path", "$userPath;$installDir", "User")
    Write-Host "Added $installDir to PATH (restart terminal to take effect)"
}

# Install auth-helper
Write-Host "Installing auth helper..."
if (Get-Command pip -ErrorAction SilentlyContinue) {
    pip install -e "$installDir\auth-helper" --quiet 2>$null
} elseif (Get-Command pip3 -ErrorAction SilentlyContinue) {
    pip3 install -e "$installDir\auth-helper" --quiet 2>$null
} else {
    Write-Host "Warning: pip not found. Run manually: pip install -e $installDir\auth-helper"
}

# Cleanup
Remove-Item $tmp.FullName -Force
Remove-Item $extractDir -Recurse -Force

Write-Host ""
Write-Host "Installed storectl to $installDir"
Write-Host ""
Write-Host "Next steps:"
Write-Host "  storectl doctor"
Write-Host "  storectl auth login"
