$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$media = Join-Path $root "real_media\octopus"
$generated = Join-Path $media "generated"
New-Item -ItemType Directory -Force $media, $generated | Out-Null

$downloads = @(
    @("https://commons.wikimedia.org/wiki/Special:Redirect/file/Octopus%20Vulgaris%20-%20Poulpe%20commun.webm", (Join-Path $media "common_octopus.webm")),
    @("https://commons.wikimedia.org/wiki/Special:Redirect/file/Octopus.ogv", (Join-Path $media "reef_octopus.ogv")),
    @("https://commons.wikimedia.org/wiki/Special:Redirect/file/Octa1000.webm", (Join-Path $media "suckers_octopus.webm")),
    @("https://commons.wikimedia.org/wiki/Special:Redirect/file/Sealife-Munich-Octopus.ogv", (Join-Path $media "sealife_octopus.ogv"))
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
