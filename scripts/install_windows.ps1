[CmdletBinding()]
param([switch]$SkipPythonPackages, [switch]$SkipVideoTools)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$tools = Join-Path $root ".tools"
$cache = Join-Path $root ".cache"
$venvPython = Join-Path $root ".venv\Scripts\python.exe"
New-Item -ItemType Directory -Force -Path $tools, $cache | Out-Null

function Write-Step([string]$Message) { Write-Host "`n==> $Message" -ForegroundColor Cyan }

function Test-Python([string]$Executable, [string[]]$Arguments = @()) {
    if (-not $Executable) { return $false }
    try {
        & $Executable @Arguments -c "import sys; raise SystemExit(0 if (3,10) <= sys.version_info[:2] < (3,13) else 1)" *> $null
        return $LASTEXITCODE -eq 0
    } catch { return $false }
}

function Find-Python {
    $candidates = [System.Collections.Generic.List[object]]::new()
    $command = Get-Command python.exe -ErrorAction SilentlyContinue
    if ($command) { $candidates.Add([pscustomobject]@{ Exe=$command.Source; Args=[string[]]@() }) }
    foreach ($path in @(
        (Join-Path $env:LOCALAPPDATA "Programs\Python\Python312\python.exe"),
        (Join-Path $env:LOCALAPPDATA "Programs\Python\Python311\python.exe"),
        (Join-Path $env:LOCALAPPDATA "Programs\Python\Python310\python.exe")
    )) { if (Test-Path $path) { $candidates.Add([pscustomobject]@{ Exe=$path; Args=[string[]]@() }) } }
    $launcher = Get-Command py.exe -ErrorAction SilentlyContinue
    if ($launcher) {
        foreach ($version in @("-3.12", "-3.11", "-3.10")) {
            $candidates.Add([pscustomobject]@{ Exe=$launcher.Source; Args=[string[]]@($version) })
        }
    }
    foreach ($candidate in $candidates) {
        if (Test-Python $candidate.Exe $candidate.Args) { return $candidate }
    }
    return $null
}

function Get-Download([string]$Uri, [string]$Destination, [string]$Sha256) {
    if (Test-Path $Destination) {
        $current = (Get-FileHash -Algorithm SHA256 -LiteralPath $Destination).Hash.ToLowerInvariant()
        if ($current -eq $Sha256) { return }
    }
    $partial = "$Destination.partial"
    Remove-Item -LiteralPath $partial -Force -ErrorAction SilentlyContinue
    & curl.exe --fail --location --retry 3 --output $partial $Uri
    if ($LASTEXITCODE -ne 0) { throw "No se pudo descargar $Uri" }
    $actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $partial).Hash.ToLowerInvariant()
    if ($actual -ne $Sha256) { throw "La descarga no superó la verificación SHA-256: $Uri" }
    Move-Item -LiteralPath $partial -Destination $Destination -Force
}

Set-Location $root
Write-Step "Comprobando Python 3.10-3.12"
$python = Find-Python
if (-not $python) {
    $winget = Get-Command winget.exe -ErrorAction SilentlyContinue
    if (-not $winget) {
        throw "No se encontró Python compatible ni winget. Instala Python 3.11 desde python.org, marca 'Add Python to PATH' y vuelve a ejecutar INSTALAR.bat."
    }
    Write-Host "Python no está instalado. Se instalará Python 3.11 para el usuario actual."
    & $winget.Source install --id Python.Python.3.11 --exact --scope user --silent --accept-package-agreements --accept-source-agreements
    if ($LASTEXITCODE -ne 0) { throw "winget no pudo instalar Python 3.11." }
    $python = Find-Python
    if (-not $python) { throw "Python se instaló, pero aún no se puede localizar. Cierra esta ventana y ejecuta INSTALAR.bat de nuevo." }
}
Write-Host "Python: $($python.Exe) $($python.Args -join ' ')"

if (-not $SkipPythonPackages) {
    Write-Step "Creando el entorno aislado"
    if (-not (Test-Path $venvPython)) {
        & $python.Exe @($python.Args) -m venv (Join-Path $root ".venv")
        if ($LASTEXITCODE -ne 0) { throw "No se pudo crear .venv" }
    }
    Write-Step "Instalando la aplicación"
    & $venvPython -m pip install --disable-pip-version-check --upgrade pip
    if ($LASTEXITCODE -ne 0) { throw "No se pudo actualizar pip" }
    & $venvPython -m pip install --disable-pip-version-check -r (Join-Path $root "requirements.txt")
    if ($LASTEXITCODE -ne 0) { throw "No se pudieron instalar las dependencias de AutoShorts" }
}

if (-not $SkipVideoTools) {
    Write-Step "Instalando FFmpeg"
    $ffmpeg = Get-ChildItem $tools -Filter "ffmpeg*.exe" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $ffmpeg) {
        $wheel = Join-Path $cache "imageio_ffmpeg-0.6.0-py3-none-win_amd64.whl"
        Get-Download "https://files.pythonhosted.org/packages/2c/c6/fa760e12a2483469e2bf5058c5faff664acf66cadb4df2ad6205b016a73d/imageio_ffmpeg-0.6.0-py3-none-win_amd64.whl" $wheel "02fa47c83703c37df6bfe4896aab339013f62bf02c5ebf2dce6da56af04ffc0a"
        $ffmpegDir = Join-Path $tools "imageio_ffmpeg"
        New-Item -ItemType Directory -Force -Path $ffmpegDir | Out-Null
        & tar.exe -xf $wheel -C $ffmpegDir
        if ($LASTEXITCODE -ne 0) { throw "No se pudo extraer FFmpeg" }
    }

    Write-Step "Instalando la narración local Piper"
    $piperRoot = Join-Path $tools "piper"
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
