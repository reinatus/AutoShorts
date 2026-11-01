$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$media = Join-Path $root "real_media"
$stills = Join-Path $media "stills"
$generated = Join-Path $media "generated"
New-Item -ItemType Directory -Force $stills, $generated | Out-Null

$downloads = @(
    @("https://upload.wikimedia.org/wikipedia/commons/b/bd/Why_the_fastest_warming_place_on_earth_can%E2%80%99t_quit_coal.webm", (Join-Path $media "svalbard_context_news.webm")),
    @("https://commons.wikimedia.org/wiki/Special:Redirect/file/Graveyard%20of%20Longyearbyen%2C%20Svalbard%2C%20below%20coal%20mine%20no.1.jpg", (Join-Path $stills "cemetery.jpg")),
    @("https://commons.wikimedia.org/wiki/Special:Redirect/file/Svalbard%2C%20Longyearbyen%20Hospital.jpg", (Join-Path $stills "hospital.jpg"))
)

foreach ($item in $downloads) {
    if (-not (Test-Path $item[1])) {
        Write-Host "Descargando $($item[1])"
        Invoke-WebRequest -UseBasicParsing -Uri $item[0] -OutFile $item[1]
    }
}

$piper = Join-Path $root ".tools\piper\piper\piper.exe"
$model = Join-Path $root ".tools\piper\es_ES-sharvard-medium.onnx"
$narration = Join-Path $media "narracion.txt"
$wav = Join-Path $generated "narracion.wav"
if ((Test-Path $piper) -and (Test-Path $model)) {
    Get-Content $narration -Raw | & $piper --model $model --output_file $wav --speaker 0 --length_scale 1.0
    if ($LASTEXITCODE -ne 0) { throw "Piper no pudo generar la narración" }
} else {
    throw "Falta Piper o el modelo es_ES-sharvard-medium en .tools\piper. No se usará una API de pago como sustituto automático."
}

Write-Host "Medios y narración preparados. Ejecuta scripts\render_real_short.ps1."

