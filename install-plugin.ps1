# CC5 MCP Bridge Plugin Installer (run elevated once)
# CLAUDE-NOTE (2026-10-24, hoodtronik fork): upstream copied files from a hardcoded user path, so every
# plugin edit needed another elevated copy. This links OpenPlugin\CC5_MCP_Bridge to this repo's cc5-plugin
# folder with a directory junction instead: one UAC prompt, then repo edits are live after a CC5 restart.
param([string]$CC5Root = "C:\Program Files\Reallusion\Character Creator 5")

$source = Join-Path $PSScriptRoot "cc5-plugin"
$dest   = Join-Path $CC5Root "Bin64\OpenPlugin\CC5_MCP_Bridge"

if (-not (Test-Path (Join-Path $source "main.py"))) { throw "cc5-plugin\main.py not found next to this script: $source" }

if (Test-Path $dest) {
    $item = Get-Item $dest -Force
    if ($item.LinkType -eq "Junction" -or $item.LinkType -eq "SymbolicLink") {
        $item.Delete()   # removes the link only, never the repo files it points at
    } else {
        Remove-Item -Recurse -Force $dest
    }
    Write-Host "Removed old plugin entry." -ForegroundColor Yellow
}

New-Item -ItemType Junction -Path $dest -Target $source | Out-Null
Write-Host "Plugin linked: $dest -> $source" -ForegroundColor Green
Write-Host "Restart Character Creator 5 to load it." -ForegroundColor Cyan
