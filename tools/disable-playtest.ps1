$ErrorActionPreference = 'Stop'
if (Get-Process -Name hl2 -ErrorAction SilentlyContinue) {
    throw 'Close Half-Life 2 first so the preview can be disabled safely.'
}
if (Get-Process -Name xenesthesia-toggle -ErrorAction SilentlyContinue) {
    throw 'Wait for the preview companion to close before disabling the addon.'
}
$steamPath = (Get-ItemProperty -LiteralPath 'HKCU:\Software\Valve\Steam').SteamPath
$game = [IO.Path]::GetFullPath((Join-Path $steamPath 'steamapps\common\Half-Life 2'))
$preview = [IO.Path]::GetFullPath((Join-Path $game 'hl2\custom\xenesthesia_playtest.vpk'))
$saved = [IO.Path]::GetFullPath((Join-Path $game 'xenesthesia_playtest.vpk.disabled'))
if (-not $preview.StartsWith($game + '\') -or -not $saved.StartsWith($game + '\')) {
    throw 'Unexpected preview path.'
}
if (Test-Path -LiteralPath $preview) {
    Move-Item -LiteralPath $preview -Destination $saved -Force
}
$live = [IO.Path]::GetFullPath((Join-Path $game 'hl2\custom\aa_xenesthesia_live'))
$liveSaved = [IO.Path]::GetFullPath((Join-Path $game 'xenesthesia_live.disabled'))
if (-not $live.StartsWith($game + '\') -or -not $liveSaved.StartsWith($game + '\')) { throw 'Unexpected live toggle path.' }
if (Test-Path -LiteralPath $live) {
    if ([IO.File]::ReadAllText((Join-Path $live '.xenesthesia-owned')).Trim() -ne 'Xenesthesia live toggle v1') { throw 'Unowned live toggle directory.' }
    if (Test-Path -LiteralPath $liveSaved) { throw 'A disabled live preview already exists; retain it and inspect before replacing.' }
    Move-Item -LiteralPath $live -Destination $liveSaved
}
Write-Output 'Xenesthesia preview disabled. Start Half-Life 2 normally. Run install-playtest.ps1 to re-enable it.'
Write-Output 'This removes the visual addon only. Restore your preferred video settings and F4/F6/F8 bindings in Options if desired.'
