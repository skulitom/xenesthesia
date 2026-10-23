$ErrorActionPreference = 'Stop'
$project = Split-Path -Parent $PSScriptRoot
$steamPath = (Get-ItemProperty -LiteralPath 'HKCU:\Software\Valve\Steam').SteamPath
$install = Join-Path $steamPath 'steamapps\common\Half-Life 2'
$cfg = Join-Path $install 'hl2_complete\cfg'
$custom = Join-Path $install 'hl2\custom'
if (Get-Process -Name hl2 -ErrorAction SilentlyContinue) { throw 'Close Half-Life 2 before preparing the preview.' }
if (-not (Test-Path -LiteralPath (Join-Path $cfg 'workshop.txt'))) { throw 'Expected installed Half-Life 2 Workshop settings.' }
$backup = Join-Path $project 'artifacts\private\native-playtest-backup'
New-Item -ItemType Directory -Path $backup,$custom -Force | Out-Null
foreach ($name in @('workshop.txt','config.cfg')) {
    $original = Join-Path $cfg $name
    $saved = Join-Path $backup $name
    if (-not (Test-Path -LiteralPath $saved)) { Copy-Item -LiteralPath $original -Destination $saved }
}
$encoding = New-Object System.Text.UTF8Encoding $false
$workshop = Join-Path $cfg 'workshop.txt'
$settings = [IO.File]::ReadAllText($workshop)
if ($settings -notmatch '"3822268020"\s+"[01]"') { throw 'Expected City 17 ASCII entry; inspect Workshop settings before changing them.' }
# Preserve the subscription and every other addon setting; disable only ASCII.
$settings = $settings -replace '("3822268020"\s+)"[01]"', '${1}"0"'
[IO.File]::WriteAllText($workshop,$settings,$encoding)
$config = Join-Path $cfg 'config.cfg'
$settings = [IO.File]::ReadAllText($config)
if ($settings -notmatch '(?m)^hl2_expansion\s+"[^"]*"') { throw 'Expected native campaign setting.' }
$settings = $settings -replace '(?m)^hl2_expansion\s+"[^"]*"', 'hl2_expansion "hl2"'
[IO.File]::WriteAllText($config,$settings,$encoding)
$target = Join-Path $custom 'xenesthesia_playtest.vpk'
Copy-Item -LiteralPath (Join-Path $project 'content.vpk') -Destination $target
if ((Get-FileHash -LiteralPath $target).Hash -ne (Get-FileHash -LiteralPath (Join-Path $project 'content.vpk')).Hash) { throw 'Preview copy verification failed.' }
$previewConfig = @'
hl2_expansion hl2
mat_hdr_level 2
mat_antialias 0
mat_aaquality 0
bind F6 gameui_activate
bind F8 toggleconsole
exec xen_keys
'@
[IO.File]::WriteAllText((Join-Path $cfg 'xen_preview.cfg'),$previewConfig,$encoding)
Write-Output 'Native HL2 preview installed; ASCII disabled, subscription retained. Original settings backed up.'
