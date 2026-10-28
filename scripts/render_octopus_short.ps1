param(
    [string]$Output = "..\..\outputs\AutoShorts-Pulpo-neuronas-FINAL.mp4",
    [ValidateRange(0,3)]
    [int]$CtaVariant = 0
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$ffmpeg = (Get-ChildItem (Join-Path $root ".tools") -Filter "ffmpeg*.exe" -Recurse | Select-Object -First 1).FullName
if (-not $ffmpeg) { throw "FFmpeg no encontrado" }

$media = Join-Path $root "real_media\octopus"
$temp = Join-Path $root ".tmp\octopus-short"
New-Item -ItemType Directory -Force $temp | Out-Null

# Rota la llamada final entre Shorts sin cambiar el montaje ni los subtitulos a mano.
$ctaVariants = @(
    "¿TÚ QUÉ PIENSAS?\NDEJA TU COMENTARIO ↓",
    "¿TE HA SORPRENDIDO?\NCUÉNTAME POR QUÉ ↓",
    "¿LO SABÍAS?\NTE LEO EN COMENTARIOS ↓",
    "¿QUÉ HARÍAS TÚ?\NDEJA TU RESPUESTA ↓"
)
$subtitleTemplate = Get-Content -Raw (Join-Path $media "subtitles.ass")
$renderSubtitles = Join-Path $temp "subtitles_render.ass"
$subtitleTemplate.Replace("{{CTA_FINAL}}", $ctaVariants[$CtaVariant]) | Set-Content -Encoding utf8 $renderSubtitles

$segments = @(
    # Macro real de brazos y ventosas desde el primer fotograma.
    @{ Name="01"; Source="suckers_octopus.webm"; Start=0.0;  Duration=4.0; X="770" },
    @{ Name="02"; Source="sealife_octopus.ogv";  Start=0.0;  Duration=4.0; X="1166" },
    # Primer plano de brazos: la infografia neuronal se anade despues en ASS.
    @{ Name="03"; Source="suckers_octopus.webm"; Start=12.0; Duration=4.0; X="770" },
    @{ Name="04"; Source="common_octopus.webm";  Start=4.0;  Duration=4.0; X="1100" },
    @{ Name="05"; Source="reef_octopus.ogv";     Start=28.0; Duration=4.0; X="750" },
    @{ Name="06"; Source="common_octopus.webm";  Start=20.0; Duration=4.0; X="1100" },
    @{ Name="07"; Source="sealife_octopus.ogv";  Start=8.0;  Duration=4.0; X="1166" },
    @{ Name="08"; Source="common_octopus.webm";  Start=40.0; Duration=4.0; X="1100" },
    @{ Name="09"; Source="reef_octopus.ogv";     Start=44.0; Duration=4.0; X="750" },
    @{ Name="10"; Source="common_octopus.webm";  Start=32.0; Duration=4.0; X="1100" }
)

foreach ($segment in $segments) {
    $source = Join-Path $media $segment.Source
    $target = Join-Path $temp ("{0}.mp4" -f $segment.Name)
    $deinterlace = if ($segment.Source -eq "suckers_octopus.webm") { "bwdif=mode=send_frame:parity=auto:deint=all," } else { "" }
    & $ffmpeg -y -hide_banner -loglevel error -ss $segment.Start -i $source -t $segment.Duration -an `
        -vf ($deinterlace + "scale=-2:1920,crop=1080:1920:$($segment.X):0,setsar=1,fps=30,eq=contrast=1.05:saturation=1.08,format=yuv420p") `
        -c:v libx264 -preset veryfast -crf 18 $target
    if ($LASTEXITCODE -ne 0) { throw "Falló el segmento $($segment.Name)" }
}

$voiceInputs = @()
for ($i=1; $i -le 11; $i++) {
    $voiceInputs += @("-i", (Join-Path $media ("generated\phrase_{0:D2}.wav" -f $i)))
}
$voiceTags = (0..10 | ForEach-Object { "[$($_):a]" }) -join ""
& $ffmpeg -y -hide_banner -loglevel error @voiceInputs -filter_complex ($voiceTags + "concat=n=11:v=0:a=1[a]") `
    -map "[a]" -c:a pcm_s16le (Join-Path $temp "narracion.wav")
if ($LASTEXITCODE -ne 0) { throw "Falló el ensamblado de la narración" }

$videoInputs = @()
for ($i=1; $i -le 10; $i++) {
    $videoInputs += @("-i", (Join-Path $temp ("{0:D2}.mp4" -f $i)))
}
$videoTags = (0..9 | ForEach-Object { "[$($_):v]" }) -join ""
$subs = $renderSubtitles.Replace('\','/').Replace(':','\:')
$filter = $videoTags + "concat=n=10:v=1:a=0,trim=duration=39.85,setpts=PTS-STARTPTS,ass='$subs'[v]"
$outputPath = if ([System.IO.Path]::IsPathRooted($Output)) {
    [System.IO.Path]::GetFullPath($Output)
}
else {
    [System.IO.Path]::GetFullPath((Join-Path $root $Output))
}
New-Item -ItemType Directory -Force (Split-Path -Parent $outputPath) | Out-Null

& $ffmpeg -y -hide_banner -loglevel error @videoInputs -i (Join-Path $temp "narracion.wav") `
    -filter_complex $filter -map "[v]" -map "10:a" -t 39.85 `
    -c:v libx264 -preset medium -crf 18 -profile:v high -level 4.1 `
    -af "volume=-1.5dB,alimiter=limit=0.92" -c:a aac -b:a 192k -ar 48000 -movflags +faststart $outputPath
if ($LASTEXITCODE -ne 0) { throw "Falló el ensamblado final" }

Write-Host "Vídeo creado: $outputPath"
