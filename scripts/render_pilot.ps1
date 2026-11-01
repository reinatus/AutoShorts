[CmdletBinding()]
param([switch]$KeepAvi)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$project = Join-Path $root "godot_pilot"
$output = Join-Path $project "output"
New-Item -ItemType Directory -Force -Path $output | Out-Null

$godot = Get-ChildItem -Path (Join-Path $root ".tools") -Filter "Godot*_console.exe" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $godot) {
    throw "Godot no está preparado. Ejecuta primero INSTALAR_PILOTO.bat"
}
$ffmpeg = Get-ChildItem -Path (Join-Path $root ".tools") -Filter "ffmpeg*.exe" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
$ffprobe = Get-ChildItem -Path (Join-Path $root ".tools") -Filter "ffprobe.exe" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1

$avi = Join-Path $output "autoshorts_pilot.avi"
$mp4 = Join-Path $output "autoshorts_pilot.mp4"
Remove-Item -LiteralPath $avi, $mp4 -Force -ErrorAction SilentlyContinue

Write-Host "Renderizando 40 s de animación procedural a 1080x1920 / 30 fps..."
& $godot.FullName --path $project --write-movie $avi --fixed-fps 30 --quit-after 1200 --resolution 1080x1920 --display-driver windows
if ($LASTEXITCODE -ne 0 -or -not (Test-Path $avi)) {
    throw "Godot no produjo el AVI esperado (código $LASTEXITCODE)"
}

if (-not $ffmpeg) {
    Write-Warning "FFmpeg no está disponible. El piloto verificable queda en $avi"
    exit 0
}

Write-Host "Codificando MP4 H.264..."
& $ffmpeg.FullName -y -hide_banner -loglevel warning -i $avi -t 40 -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -c:a aac -b:a 128k -movflags +faststart $mp4
if ($LASTEXITCODE -ne 0 -or -not (Test-Path $mp4)) {
    throw "FFmpeg no produjo el MP4 esperado (código $LASTEXITCODE)"
}

if ($ffprobe) {
    Write-Host "Verificación del resultado:"
    & $ffprobe.FullName -v error -show_entries format=duration:stream=codec_name,width,height,r_frame_rate -of default=noprint_wrappers=1 $mp4
    if ($LASTEXITCODE -ne 0) { throw "ffprobe no pudo validar el MP4" }
}
else {
    & $ffmpeg.FullName -v error -i $mp4 -t 0.10 -f null NUL
    if ($LASTEXITCODE -ne 0) { throw "FFmpeg no pudo validar el MP4" }
    $previousPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $details = (& $ffmpeg.FullName -hide_banner -i $mp4 2>&1 | Out-String)
    $ErrorActionPreference = $previousPreference
    if ($details -notmatch "Duration: 00:00:40\.00" -or $details -notmatch "1080x1920" -or $details -notmatch "30 fps") {
        throw "El MP4 no cumple duración, dimensiones o fps esperados: $details"
    }
    Write-Host "MP4 verificado: H.264/AAC, 1080x1920, 30 fps, 40,00 s."
}

if (-not $KeepAvi) { Remove-Item -LiteralPath $avi -Force }
Write-Host "Piloto terminado: $mp4"

