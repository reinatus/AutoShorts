param(
    [string]$Output = "..\..\outputs\AutoShorts-Svalbard-real-v1.mp4"
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$ffmpeg = (Get-ChildItem (Join-Path $root ".tools") -Filter "ffmpeg*.exe" -Recurse | Select-Object -First 1).FullName
if (-not $ffmpeg) { throw "FFmpeg no encontrado. Ejecuta primero INSTALAR_PILOTO.bat." }

$source = Join-Path $root "real_media\svalbard_context_news.webm"
$cemetery = Join-Path $root "real_media\stills\cemetery.jpg"
$hospital = Join-Path $root "real_media\stills\hospital.jpg"
$voice = Join-Path $root "real_media\generated\narracion.wav"
$subs = Join-Path $root "real_media\subtitles.ass"
$temp = Join-Path $root ".tmp\real-short"
New-Item -ItemType Directory -Force $temp | Out-Null

$segments = @(
    @{ Name="01"; Start=265.0; Duration=3.5; X="250" },
    @{ Name="02"; Start=178.0; Duration=4.5; X="(iw-ow)/2" },
    @{ Name="03"; Start=297.0; Duration=4.2; X="(iw-ow)/2" },
    @{ Name="04"; Start=210.0; Duration=4.5; X="(iw-ow)/2" },
    @{ Name="07"; Start=448.0; Duration=3.5; X="(iw-ow)/2" },
    @{ Name="09"; Start=39.5;  Duration=3.5; X="(iw-ow)/2" },
    @{ Name="10"; Start=265.0; Duration=3.3; X="1000" }
)

foreach ($segment in $segments) {
    $target = Join-Path $temp ("{0}.mp4" -f $segment.Name)
    & $ffmpeg -y -hide_banner -loglevel error -ss $segment.Start -i $source -t $segment.Duration `
        -an -vf "scale=-2:1920,crop=1080:1920:$($segment.X):0,setsar=1,fps=30,eq=contrast=1.04:saturation=0.95,format=yuv420p" `
        -c:v libx264 -preset veryfast -crf 19 $target
    if ($LASTEXITCODE -ne 0) { throw "Falló el segmento $($segment.Name)" }
}

& $ffmpeg -y -hide_banner -loglevel error -loop 1 -i $cemetery -t 5.1 -an `
    -vf "scale=-2:1920,crop=1080:1920:(iw-ow)/2:0,setsar=1,fps=30,eq=contrast=1.04:saturation=0.92,format=yuv420p" `
    -c:v libx264 -preset veryfast -crf 19 (Join-Path $temp "05.mp4")
if ($LASTEXITCODE -ne 0) { throw "Falló la fotografía del cementerio" }

& $ffmpeg -y -hide_banner -loglevel error -loop 1 -i $cemetery -t 3.9 -an `
    -vf "crop=2300:3000:650:2400,scale=1080:1920,setsar=1,fps=30,eq=contrast=1.06:saturation=0.9,format=yuv420p" `
    -c:v libx264 -preset veryfast -crf 19 (Join-Path $temp "06.mp4")
if ($LASTEXITCODE -ne 0) { throw "Falló el detalle del cementerio" }

& $ffmpeg -y -hide_banner -loglevel error -loop 1 -i $hospital -t 4.0 -an `
    -vf "scale=-2:1920,crop=1080:1920:1000:0,setsar=1,fps=30,eq=contrast=1.03:saturation=0.92,format=yuv420p" `
    -c:v libx264 -preset veryfast -crf 19 (Join-Path $temp "08.mp4")
if ($LASTEXITCODE -ne 0) { throw "Falló la fotografía del hospital" }

$ordered = 1..10 | ForEach-Object { Join-Path $temp ("{0:D2}.mp4" -f $_) }
$inputs = @()
foreach ($item in $ordered) { $inputs += @("-i", $item) }
$concat = (0..9 | ForEach-Object { "[$($_):v]" }) -join ""
$filter = "$concat" + "concat=n=10:v=1:a=0,trim=duration=40,setpts=PTS-STARTPTS,ass='$($subs.Replace('\','/').Replace(':','\:'))'[v]"
$outputPath = [System.IO.Path]::GetFullPath((Join-Path $root $Output))
New-Item -ItemType Directory -Force (Split-Path -Parent $outputPath) | Out-Null

& $ffmpeg -y -hide_banner -loglevel error @inputs -i $voice -filter_complex $filter `
    -map "[v]" -map "10:a" -t 40 -c:v libx264 -preset medium -crf 18 -profile:v high -level 4.1 `
    -c:a aac -b:a 192k -ar 48000 -movflags +faststart $outputPath
if ($LASTEXITCODE -ne 0) { throw "Falló el ensamblado final" }

Write-Host "Video creado: $outputPath"

