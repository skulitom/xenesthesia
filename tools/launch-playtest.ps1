param([ValidateSet('coast','ravenholm')][string]$Scene = 'coast')
$ErrorActionPreference = 'Stop'
$project = Split-Path -Parent $PSScriptRoot
$game = Join-Path $project 'testgame'
if (-not (Test-Path -LiteralPath (Join-Path $game 'gameinfo.txt'))) {
    throw 'The isolated local playtest folder has not been prepared on this machine.'
}
if (Get-Process -Name hl2 -ErrorAction SilentlyContinue) {
    throw 'Close the running Half-Life 2 before launching this preview.'
}
$steamPath = (Get-ItemProperty -LiteralPath 'HKCU:\Software\Valve\Steam').SteamPath
$steam = Join-Path $steamPath 'steam.exe'
$currentSession = [System.Diagnostics.Process]::GetCurrentProcess().SessionId
$client = Get-Process -Name steam -ErrorAction SilentlyContinue | Where-Object SessionId -eq $currentSession
if (-not $client) { throw 'Run this launcher on your normal desktop with Steam signed in there.' }
$save = if ($Scene -eq 'coast') { 'xen_coast' } else { 'xen_night' }
$map = if ($Scene -eq 'coast') { 'd2_coast_03' } else { 'd1_town_01' }
$start = if (Test-Path -LiteralPath (Join-Path $game "save\$save.sav")) { "+load $save" } else { "+map $map" }
# The user explicitly requests an interactive game window on their own desktop.
Start-Process -FilePath $steam -ArgumentList ('-applaunch 220 -game "{0}" -windowed -noborder -w 1920 -h 1080 -novid -condebug {1}' -f $game,$start)
Write-Output 'Xenesthesia preview requested on your desktop. F4 toggles the effect.'
