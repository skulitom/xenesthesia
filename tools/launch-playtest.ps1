param([ValidateSet('menu','coast','ravenholm')][string]$Scene = 'menu')
$ErrorActionPreference = 'Stop'
$project = Split-Path -Parent $PSScriptRoot
if (Get-Process -Name hl2 -ErrorAction SilentlyContinue) {
    throw 'Close the running Half-Life 2 before launching this preview.'
}
$steamPath = (Get-ItemProperty -LiteralPath 'HKCU:\Software\Valve\Steam').SteamPath
$steam = Join-Path $steamPath 'steam.exe'
$game = Join-Path $steamPath 'steamapps\common\Half-Life 2'
if (-not (Test-Path -LiteralPath (Join-Path $game 'hl2\custom\xenesthesia_playtest.vpk'))) {
    throw 'Run install-playtest.ps1 first to prepare the native preview.'
}
$currentSession = [System.Diagnostics.Process]::GetCurrentProcess().SessionId
$client = Get-Process -Name steam -ErrorAction SilentlyContinue | Where-Object SessionId -eq $currentSession
if (-not $client) { throw 'Run this launcher on your normal desktop with Steam signed in there.' }
$start = ''
if ($Scene -ne 'menu') {
    $map = if ($Scene -eq 'coast') { 'd2_coast_03' } else { 'd1_town_01' }
    $start = "+map $map"
}
# The user explicitly requests an interactive game window on their own desktop.
# Start at the menu by default so opening the preview cannot immediately grab
# the mouse for gameplay. Keep the title bar and normal window controls.
# Use the installed executable with the existing signed-in Steam client. This
# also leaves any unresolved Steam Cloud config choice untouched.
$preview = Start-Process -FilePath (Join-Path $game 'hl2.exe') -WorkingDirectory $game -ArgumentList ('-steam -game hl2_complete -windowed -w 1280 -h 720 -novid -condebug +hl2_expansion hl2 +exec xen_preview {0}' -f $start) -PassThru
& (Join-Path $PSScriptRoot 'start-live-toggle.ps1') -GameProcessId $preview.Id
Write-Output 'Xenesthesia preview opened in a bordered window. F5 switches all mod visuals off/on with a brief material refresh. F6 pauses and releases the mouse.'
