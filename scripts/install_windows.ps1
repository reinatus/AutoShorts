[CmdletBinding()]
param([switch]$SkipPythonPackages, [switch]$SkipVideoTools)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
$root = Split-Path -Parent $PSScriptRoot
$toolsDir = Join-Path $root ".tools"
$cache = Join-Path $root ".cache"
$runtime = Join-Path $root ".runtime"
$venv = Join-Path $runtime "venv"
$pythonRecord = Join-Path $runtime "python-path.txt"
New-Item -ItemType Directory -Force -Path $toolsDir, $cache, $runtime | Out-Null

function Write-Step([string]$Message) { Write-Host "`n==> $Message" -ForegroundColor Cyan }

function Get-Download([string]$Uri, [string]$Destination, [string]$Sha256) {
    if (Test-Path $Destination) {
        $current = (Get-FileHash -Algorithm SHA256 -LiteralPath $Destination).Hash.ToLowerInvariant()
        if ($current -eq $Sha256) { return }
    }
    Remove-Item -LiteralPath $Destination -Force -ErrorAction SilentlyContinue
    & curl.exe --fail --location --retry 3 --output $Destination $Uri
    if ($LASTEXITCODE -ne 0) { throw "No se pudo descargar $Uri" }
    $actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $Destination).Hash.ToLowerInvariant()
    if ($actual -ne $Sha256) {
        Remove-Item -LiteralPath $Destination -Force -ErrorAction SilentlyContinue
        throw "La descarga no superó la verificación SHA-256: $Uri"
    }
}

Set-Location $root
Write-Step "Preparando el runtime autocontenido"
$uvRoot = Join-Path $toolsDir "uv"
$uvExe = Join-Path $uvRoot "uv.exe"
if (-not (Test-Path $uvExe)) {
    $uvZip = Join-Path $cache "uv-x86_64-pc-windows-msvc-0.13.6.zip"
    Get-Download "https://github.com/astral-sh/uv/releases/download/0.13.6/uv-x86_64-pc-windows-msvc.zip" $uvZip "a2a8820d5eea32f08ef467ef3b7f66883a9b076d5737a2fc2fbb5f458d1bb50f"
    if (Test-Path $uvRoot) { Remove-Item -LiteralPath $uvRoot -Recurse -Force }
    New-Item -ItemType Directory -Force -Path $uvRoot | Out-Null
    Expand-Archive -LiteralPath $uvZip -DestinationPath $uvRoot -Force
    $foundUv = Get-ChildItem $uvRoot -Filter "uv.exe" -Recurse | Select-Object -First 1
    if (-not $foundUv) { throw "No se encontró uv.exe dentro del paquete descargado." }
    if ($foundUv.FullName -ne $uvExe) { Copy-Item -LiteralPath $foundUv.FullName -Destination $uvExe -Force }
}

$env:UV_CACHE_DIR = Join-Path $cache "uv"
$env:UV_LINK_MODE = "copy"
$pythonRoot = Join-Path $runtime "python-embed"
$venvPython = Join-Path $pythonRoot "python.exe"

if (-not $SkipPythonPackages) {
    Write-Step "Instalando Python portátil y dependencias"
    if (-not (Test-Path $venvPython)) {
        $pythonZip = Join-Path $cache "python-3.11.9-embed-amd64.zip"
        Get-Download "https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip" $pythonZip "009d6bf7e3b2ddca3d784fa09f90fe54336d5b60f0e0f305c37f400bf83cfd3b"
        New-Item -ItemType Directory -Force -Path $pythonRoot | Out-Null
        Expand-Archive -LiteralPath $pythonZip -DestinationPath $pythonRoot -Force
        $pth = Join-Path $pythonRoot "python311._pth"
        $pthContent = Get-Content -LiteralPath $pth -Raw
        $pthContent = $pthContent -replace "#import site", "Lib\\site-packages`r`nimport site"
        [IO.File]::WriteAllText($pth, $pthContent)
        New-Item -ItemType Directory -Force -Path (Join-Path $pythonRoot "Lib\site-packages") | Out-Null
    }
    & $uvExe pip install --python $venvPython -r (Join-Path $root "requirements.txt")
    if ($LASTEXITCODE -ne 0) { throw "No se pudieron instalar las dependencias de AutoShorts." }
}
if (-not (Test-Path $venvPython)) { throw "Falta el Python portátil. Vuelve a ejecutar INSTALAR.bat sin opciones." }
[IO.File]::WriteAllText($pythonRecord, $venvPython)
Write-Host "Runtime: $venvPython"

if (-not $SkipVideoTools) {
    Write-Step "Instalando FFmpeg"
    $ffmpeg = Get-ChildItem $toolsDir -Filter "ffmpeg*.exe" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $ffmpeg) {
        $wheel = Join-Path $cache "imageio_ffmpeg-0.6.0-py3-none-win_amd64.whl"
        Get-Download "https://files.pythonhosted.org/packages/2c/c6/fa760e12a2483469e2bf5058c5faff664acf66cadb4df2ad6205b016a73d/imageio_ffmpeg-0.6.0-py3-none-win_amd64.whl" $wheel "02fa47c83703c37df6bfe4896aab339013f62bf02c5ebf2dce6da56af04ffc0a"
        $ffmpegDir = Join-Path $toolsDir "imageio_ffmpeg"
        New-Item -ItemType Directory -Force -Path $ffmpegDir | Out-Null
        & tar.exe -xf $wheel -C $ffmpegDir
        if ($LASTEXITCODE -ne 0) { throw "No se pudo extraer FFmpeg." }
    }

    Write-Step "Instalando la narración local Piper"
    $piperRoot = Join-Path $toolsDir "piper"
    $piperExe = Join-Path $piperRoot "piper\piper.exe"
    if (-not (Test-Path $piperExe)) {
        $piperZip = Join-Path $cache "piper_windows_amd64.zip"
        Get-Download "https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_windows_amd64.zip" $piperZip "f3c58906402b24f3a96d92145f58acba6d86c9b5db896d207f78dc80811efcea"
        New-Item -ItemType Directory -Force -Path $piperRoot | Out-Null
        Expand-Archive -LiteralPath $piperZip -DestinationPath $piperRoot -Force
    }
    $voiceBase = "https://huggingface.co/rhasspy/piper-voices/resolve/320d5f7f7751a17ef6512d5c23863056c6a11c0f/es/es_ES/sharvard/medium"
    Get-Download "$voiceBase/es_ES-sharvard-medium.onnx" (Join-Path $piperRoot "es_ES-sharvard-medium.onnx") "40febfb1679c69a4505ff311dc136e121e3419a13a290ef264fdf43ddedd0fb1"
    Get-Download "$voiceBase/es_ES-sharvard-medium.onnx.json" (Join-Path $piperRoot "es_ES-sharvard-medium.onnx.json") "7438c9b699c72b0c3388dae1b68d3f364dc66a2150fe554a1c11f03372957b2c"
}

Write-Step "Verificando la instalación"
& (Join-Path $PSScriptRoot "doctor.ps1") -Quiet
if ($LASTEXITCODE -ne 0) { throw "La verificación final encontró errores." }
Write-Host "`nAutoShorts está instalado correctamente." -ForegroundColor Green
Write-Host "Ejecuta INICIAR.bat para abrirlo."
