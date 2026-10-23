param(
    [string]$Output = "..\..\outputs\AutoShorts-Pulpo-neuronas-FINAL.mp4"
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$ffmpeg = (Get-ChildItem (Join-Path $root ".tools") -Filter "ffmpeg*.exe" -Recurse | Select-Object -First 1).FullName
if (-not $ffmpeg) { throw "FFmpeg no encontrado" }

$media = Join-Path $root "real_media\octopus"
$temp = Join-Path $root ".tmp\octopus-short"
New-Item -ItemType Directory -Force $temp | Out-Null

$segments = @(
    @{ Name="01"; Source="hairy_octopus.webm";         Start=0.0;  Duration=4.0; X="950" },
    @{ Name="02"; Source="octopus_garden.webm";        Start=42.0; Duration=4.0; X="1700" },
    @{ Name="03"; Source="giant_pacific_octopus.webm"; Start=8.0;  Duration=4.0; X="2000" },
    @{ Name="04"; Source="octopus_garden.webm";        Start=46.0; Duration=4.0; X="1700" },
    @{ Name="05"; Source="hairy_octopus.webm";         Start=4.0;  Duration=4.0; X="950" },
    @{ Name="06"; Source="giant_pacific_octopus.webm"; Start=18.0; Duration=4.0; X="2000" },
    @{ Name="07"; Source="octopus_garden.webm";        Start=50.0; Duration=4.0; X="1700" },
    @{ Name="08"; Source="hairy_octopus.webm";         Start=8.0;  Duration=4.0; X="950" },
    @{ Name="09"; Source="giant_pacific_octopus.webm"; Start=28.0; Duration=4.0; X="2000" },
    @{ Name="10"; Source="octopus_garden.webm";        Start=54.0; Duration=4.0; X="1700" }
)

foreach ($segment in $segments) {
    $source = Join-Path $media $segment.Source
    $target = Join-Path $temp ("{0}.mp4" -f $segment.Name)
    & $ffmpeg -y -hide_banner -loglevel error -ss $segment.Start -i $source -t $segment.Duration -an `
        -vf "scale=-2:1920,crop=1080:1920:$($segment.X):0,setsar=1,fps=30,eq=contrast=1.05:saturation=1.08,format=yuv420p" `
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
$subs = (Join-Path $media "subtitles.ass").Replace('\','/').Replace(':','\:')
$filter = $videoTags + "concat=n=10:v=1:a=0,trim=duration=39.85,setpts=PTS-STARTPTS,ass='$subs'[v]"
$outputPath = [System.IO.Path]::GetFullPath((Join-Path $root $Output))
New-Item -ItemType Directory -Force (Split-Path -Parent $outputPath) | Out-Null

& $ffmpeg -y -hide_banner -loglevel error @videoInputs -i (Join-Path $temp "narracion.wav") `
    -filter_complex $filter -map "[v]" -map "10:a" -t 39.85 `
    -c:v libx264 -preset medium -crf 18 -profile:v high -level 4.1 `
    -af "volume=-1.5dB,alimiter=limit=0.92" -c:a aac -b:a 192k -ar 48000 -movflags +faststart $outputPath
if ($LASTEXITCODE -ne 0) { throw "Falló el ensamblado final" }

Write-Host "Vídeo creado: $outputPath"

