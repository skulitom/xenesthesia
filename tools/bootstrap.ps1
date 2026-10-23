$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$compilerPath = Join-Path $PSScriptRoot 'ShaderCompile2.exe'
$expectedHash = 'DF13601822A642D1238D55E65522842FD776911F9E76C9FEA1F4CFDF6F220230'
if (-not (Test-Path -LiteralPath $compilerPath)) {
    Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/ValveSoftware/source-sdk-2013/master/src/devtools/bin/ShaderCompile2.exe' -OutFile $compilerPath
}
if ((Get-FileHash -LiteralPath $compilerPath -Algorithm SHA256).Hash -ne $expectedHash) {
    throw 'Compiler hash differs from the tested SDK compiler. Review the upstream update before executing it.'
}
Write-Output 'Verified the official SDK shader compiler. Run python tools/build.py from the project folder.'
