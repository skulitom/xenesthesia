$ErrorActionPreference = 'Stop'
if (Get-Process -Name hl2 -ErrorAction SilentlyContinue) {
    throw 'Close Half-Life 2 first so the preview can be disabled safely.'
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
Write-Output 'Xenesthesia preview disabled. Start Half-Life 2 normally. Run install-playtest.ps1 to re-enable it.'
