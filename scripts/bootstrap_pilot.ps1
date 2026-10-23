[CmdletBinding()]
param([switch]$SkipFfmpeg)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$tools = Join-Path $root ".tools"
$cache = Join-Path $root ".cache"
New-Item -ItemType Directory -Force -Path $tools, $cache | Out-Null

function Get-Download([string]$Uri, [string]$Destination) {
    $partial = "$Destination.partial"
    Remove-Item -LiteralPath $partial -Force -ErrorAction SilentlyContinue
    & curl.exe --fail --location --retry 3 --output $partial $Uri
    if ($LASTEXITCODE -ne 0) { throw "Falló la descarga de $Uri" }
    Move-Item -LiteralPath $partial -Destination $Destination -Force
}

$godotVersion = "4.7.2-stable"
$godotZip = Join-Path $cache "Godot_v4.7.2-stable_win64.exe.zip"
$godotUrl = "https://github.com/godotengine/godot/releases/download/4.7.2-stable/Godot_v4.7.2-stable_win64.exe.zip"
$godotSha256 = "731980f9608d61333e5baf54a2ef17210acc7a538446c0cb9969f002aca1e953"
$godotDir = Join-Path $tools "godot-$godotVersion"

if (-not (Test-Path (Join-Path $godotDir "Godot_v4.7.2-stable_win64_console.exe"))) {
    Write-Host "Descargando Godot $godotVersion..."
    $actual = if (Test-Path $godotZip) { (Get-FileHash -Algorithm SHA256 -LiteralPath $godotZip).Hash.ToLowerInvariant() } else { "" }
    if ($actual -ne $godotSha256) { Get-Download $godotUrl $godotZip }
    $actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $godotZip).Hash.ToLowerInvariant()
    if ($actual -ne $godotSha256) {
        throw "SHA-256 de Godot incorrecto. Esperado $godotSha256; recibido $actual"
    }
    New-Item -ItemType Directory -Force -Path $godotDir | Out-Null
    Expand-Archive -LiteralPath $godotZip -DestinationPath $godotDir -Force
}

if (-not $SkipFfmpeg) {
    $ffmpeg = Get-ChildItem -Path $tools -Filter "ffmpeg*.exe" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $ffmpeg) {
        $ffmpegWheel = Join-Path $cache "imageio_ffmpeg-0.6.0-py3-none-win_amd64.whl"
        $ffmpegUrl = "https://files.pythonhosted.org/packages/2c/c6/fa760e12a2483469e2bf5058c5faff664acf66cadb4df2ad6205b016a73d/imageio_ffmpeg-0.6.0-py3-none-win_amd64.whl"
        $ffmpegSha256 = "02fa47c83703c37df6bfe4896aab339013f62bf02c5ebf2dce6da56af04ffc0a"
        Write-Host "Descargando el binario FFmpeg empaquetado por imageio-ffmpeg 0.6.0..."
        $actual = if (Test-Path $ffmpegWheel) { (Get-FileHash -Algorithm SHA256 -LiteralPath $ffmpegWheel).Hash.ToLowerInvariant() } else { "" }
        if ($actual -ne $ffmpegSha256) { Get-Download $ffmpegUrl $ffmpegWheel }
        $actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $ffmpegWheel).Hash.ToLowerInvariant()
        if ($actual -ne $ffmpegSha256) { throw "SHA-256 de imageio-ffmpeg incorrecto" }
        $ffmpegDir = Join-Path $tools "imageio-ffmpeg-0.6.0"
        New-Item -ItemType Directory -Force -Path $ffmpegDir | Out-Null
        & tar.exe -xf $ffmpegWheel -C $ffmpegDir
        if ($LASTEXITCODE -ne 0) { throw "No se pudo extraer el paquete imageio-ffmpeg" }
    }
}

Write-Host "Herramientas del piloto preparadas en $tools"

