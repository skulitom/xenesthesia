param([Parameter(Mandatory=$true)][int]$GameProcessId)
$ErrorActionPreference = 'Stop'
$project = Split-Path -Parent $PSScriptRoot
$game = 'D:\Steam\steamapps\common\Half-Life 2'
$state = Join-Path $game 'xenesthesia-live-state'
$gameProcess = Get-Process -Id $GameProcessId
if ($gameProcess.ProcessName -ne 'hl2') { throw 'Expected the Half-Life 2 preview process.' }
$arguments = @($state, (Join-Path $game 'hl2\custom\aa_xenesthesia_live'), (Join-Path $game 'hl2_complete\cfg'), (Join-Path $game 'hl2\console.log'), "$GameProcessId")
if ($arguments | Where-Object { $_.Contains('"') }) { throw 'Invalid quote in companion path.' }
$quotedArguments = ($arguments | ForEach-Object { '"' + $_ + '"' }) -join ' '
$companion = Start-Process -FilePath (Join-Path $state 'xenesthesia-toggle.exe') -ArgumentList $quotedArguments -WindowStyle Hidden -PassThru
Write-Output "F5 companion started for the preview (PID $($companion.Id))."
