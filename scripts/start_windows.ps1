[CmdletBinding()]
param([int]$Port = 8501, [switch]$NoBrowser)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$runtime = Join-Path $root ".runtime"
$pythonRecord = Join-Path $runtime "python-path.txt"
$logs = Join-Path $root "logs"

if (-not (Test-Path $pythonRecord)) { throw "AutoShorts no está instalado. Ejecuta INSTALAR.bat." }
$python = (Get-Content -LiteralPath $pythonRecord -Raw).Trim()
if (-not (Test-Path $python)) { throw "El runtime registrado ya no existe. Ejecuta INSTALAR.bat." }
& (Join-Path $PSScriptRoot "doctor.ps1") -Quiet
if ($LASTEXITCODE -ne 0) { throw "La instalación está incompleta. Ejecuta DIAGNOSTICO.bat." }

while ($Port -le 8510) {
    $occupied = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    if (-not $occupied) { break }
    $Port++
}
if ($Port -gt 8510) { throw "No hay un puerto libre entre 8501 y 8510." }

New-Item -ItemType Directory -Force -Path $logs | Out-Null
$stdout = Join-Path $logs "autoshorts-out.log"
$stderr = Join-Path $logs "autoshorts-error.log"
Remove-Item -LiteralPath $stdout, $stderr -Force -ErrorAction SilentlyContinue
$arguments = @("-m", "streamlit", "run", "app.py", "--server.address", "127.0.0.1", "--server.port", "$Port", "--server.headless", "true", "--browser.gatherUsageStats", "false")
$process = Start-Process -FilePath $python -ArgumentList $arguments -WorkingDirectory $root -WindowStyle Hidden -PassThru -RedirectStandardOutput $stdout -RedirectStandardError $stderr
$url = "http://127.0.0.1:$Port/"

$ready = $false
for ($attempt = 0; $attempt -lt 40; $attempt++) {
    if ($process.HasExited) { break }
    try {
        $response = Invoke-WebRequest -UseBasicParsing -Uri $url -TimeoutSec 2
        if ($response.StatusCode -eq 200) { $ready = $true; break }
    } catch { Start-Sleep -Milliseconds 500 }
}
if (-not $ready) {
    if (-not $process.HasExited) { Stop-Process -Id $process.Id -Force }
    Write-Host "AutoShorts no pudo arrancar." -ForegroundColor Red
    if (Test-Path $stderr) { Get-Content -LiteralPath $stderr -Tail 30 }
    throw "Consulta logs\autoshorts-error.log o ejecuta DIAGNOSTICO.bat."
}

[IO.File]::WriteAllText((Join-Path $root ".runtime-port"), "$Port")
Write-Host "AutoShorts está funcionando en $url" -ForegroundColor Green
Write-Host "Deja esta ventana abierta. Pulsa Ctrl+C para detenerlo."
if (-not $NoBrowser) { Start-Process $url }
try { Wait-Process -Id $process.Id } finally {
    if (-not $process.HasExited) { Stop-Process -Id $process.Id -Force }
}
