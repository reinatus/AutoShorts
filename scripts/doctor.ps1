[CmdletBinding()]
param([switch]$Quiet)

$root = Split-Path -Parent $PSScriptRoot
$failures = [System.Collections.Generic.List[string]]::new()
$checks = [System.Collections.Generic.List[string]]::new()

function Check([bool]$Condition, [string]$Ok, [string]$Failure) {
    if ($Condition) { $checks.Add("OK  $Ok") } else { $failures.Add("ERROR  $Failure") }
}

$python = Join-Path $root ".venv\Scripts\python.exe"
Check (Test-Path $python) "Entorno Python" "No existe .venv. Ejecuta INSTALAR.bat."
if (Test-Path $python) {
    & $python -c "import streamlit, requests, dotenv, pydantic; import autoshorts.studio" *> $null
    Check ($LASTEXITCODE -eq 0) "Dependencias Python" "Faltan dependencias. Ejecuta INSTALAR.bat."
    & $python -m compileall -q (Join-Path $root "app.py") (Join-Path $root "autoshorts")
    Check ($LASTEXITCODE -eq 0) "Código compilable" "Hay un error de sintaxis en la aplicación."
}
$ffmpeg = Get-ChildItem (Join-Path $root ".tools") -Filter "ffmpeg*.exe" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
Check ($null -ne $ffmpeg) "FFmpeg" "FFmpeg no está instalado. Ejecuta INSTALAR.bat."
Check (Test-Path (Join-Path $root ".tools\piper\piper\piper.exe")) "Piper" "Piper no está instalado. Ejecuta INSTALAR.bat."
Check (Test-Path (Join-Path $root ".tools\piper\es_ES-sharvard-medium.onnx")) "Voz española" "Falta la voz española local. Ejecuta INSTALAR.bat."
Check (Test-Path (Join-Path $root "real_media\octopus\narracion.txt")) "Plantilla del piloto" "Falta real_media\octopus\narracion.txt. Vuelve a descargar el paquete."
Check (Test-Path (Join-Path $root "app.py")) "Panel de AutoShorts" "Falta app.py. Vuelve a descargar el paquete."

$data = Join-Path $root "studio_data"
try {
    New-Item -ItemType Directory -Force -Path $data | Out-Null
    $probe = Join-Path $data ".write-test"
    [IO.File]::WriteAllText($probe, "ok")
    Remove-Item -LiteralPath $probe -Force
    $checks.Add("OK  Carpeta de datos escribible")
} catch { $failures.Add("ERROR  No se puede escribir en studio_data. Extrae AutoShorts en Documentos, no en Archivos de programa.") }

if (-not $Quiet) {
    Write-Host "`nDIAGNÓSTICO AUTOSHORTS" -ForegroundColor Cyan
    $checks | ForEach-Object { Write-Host $_ -ForegroundColor Green }
    $failures | ForEach-Object { Write-Host $_ -ForegroundColor Red }
}
if ($failures.Count -gt 0) { exit 1 }
if (-not $Quiet) { Write-Host "`nTodo preparado." -ForegroundColor Green }
exit 0
