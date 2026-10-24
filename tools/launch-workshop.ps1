# Start the real subscribed release early enough for Source's shader cache.
$ErrorActionPreference = 'Stop'
if (Get-Process hl2 -ErrorAction SilentlyContinue) { throw 'Close Half-Life 2 first.' }
$steamPath = (Get-ItemProperty -LiteralPath 'HKCU:\Software\Valve\Steam').SteamPath
$game = Join-Path $steamPath 'steamapps\common\Half-Life 2'
$package = Join-Path $steamPath 'steamapps\workshop\content\220\3826155980\workshop_dir.vpk'
if (-not (Test-Path -LiteralPath $package)) { throw 'Subscribe to Xenesthesia and wait for Steam to finish downloading it.' }
$session = [System.Diagnostics.Process]::GetCurrentProcess().SessionId
if (-not (Get-Process steam -ErrorAction SilentlyContinue | Where-Object SessionId -eq $session)) { throw 'Open Steam and sign in on this desktop first.' }
# This is an explicitly requested interactive game preview.
Start-Process -FilePath (Join-Path $game 'hl2.exe') -WorkingDirectory $game -ArgumentList ('-steam -game hl2_complete -novid -windowed -w 1280 -h 720 -insert_search_path "{0}" +hl2_expansion hl2' -f $package)
Write-Output 'Opened the subscribed Xenesthesia release. No local development VPK or companion is required.'
