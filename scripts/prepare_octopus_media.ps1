$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$media = Join-Path $root "real_media\octopus"
$generated = Join-Path $media "generated"
New-Item -ItemType Directory -Force $media, $generated | Out-Null

$downloads = @(
    @("https://commons.wikimedia.org/wiki/Special:Redirect/file/Giant%20Pacific%20Octopus%20in%20Washington.webm", (Join-Path $media "giant_pacific_octopus.webm")),
    @("https://commons.wikimedia.org/wiki/Special:Redirect/file/Hairy%20octopus.webm", (Join-Path $media "hairy_octopus.webm")),
    @("https://commons.wikimedia.org/wiki/Special:Redirect/file/Wk215-deep-sea-octopuses.webm", (Join-Path $media "octopus_garden.webm"))
)

foreach ($item in $downloads) {
    if (-not (Test-Path $item[1])) {
        Write-Host "Descargando $($item[1])"
        Invoke-WebRequest -UseBasicParsing -Uri $item[0] -OutFile $item[1]
    }
}

$piper = Join-Path $root ".tools\piper\piper\piper.exe"
$model = Join-Path $root ".tools\piper\es_ES-sharvard-medium.onnx"
if (-not ((Test-Path $piper) -and (Test-Path $model))) {
    throw "Falta Piper o el modelo es_ES-sharvard-medium. No se usará una API de pago automáticamente."
}

$lines = Get-Content (Join-Path $media "narracion.txt") | Where-Object { $_.Trim() }
for ($i = 0; $i -lt $lines.Count; $i++) {
    $target = Join-Path $generated ("phrase_{0:D2}.wav" -f ($i + 1))
    $lines[$i] | & $piper --model $model --output_file $target --speaker 0 --length_scale 0.88
    if ($LASTEXITCODE -ne 0) { throw "Piper falló en la frase $($i + 1)" }
}

Write-Host "Medios y narración preparados. Ejecuta scripts\render_octopus_short.ps1."

