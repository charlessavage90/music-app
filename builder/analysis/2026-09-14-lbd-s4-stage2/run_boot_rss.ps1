# LBA-M1 -- boot memory and the metadata_ratio calibration. ONE LOAD PER PROCESS, three repeats.
#
# PeakWorkingSetSize is a whole-process high-water mark and never falls, so two loads in one
# process would give the second one the first one's peak. Every repeat is therefore its own
# process, and this script is only the loop.
#
# WHAT IS MEASURED, and the two that are NOT arms:
#   CAL-lux4 / CAL-served  the metadata_ratio calibration pair. Identical in artist count and CSR
#                          entries; they differ only in the three LUX-4 additive keys, which is
#                          what makes the ratio isolate the metadata term.
#   LBA-A1 / LBA-A3        the two REUSED arms, measured on their BARE re-serialisations. Their
#                          only committed artifacts carry all five additive keys, and multiplying
#                          such a figure by metadata_ratio would scale metadata that is already
#                          there. See s4_bare_copy.py.
#   LBA-A2 .. LBA-A9       the census builds, which carry no additive key already.
#
# ASCII ONLY -- Windows PowerShell 5.1 reads a BOM-less UTF-8 .ps1 as ANSI.
$ErrorActionPreference = "Continue"
$env:UV_LINK_MODE = "copy"
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUNBUFFERED = "1"

$here = "C:\dev\music-app\builder"
$stage2 = "C:\dev\music-app\builder\analysis\2026-09-14-lbd-s4-stage2"
$boot = Join-Path $stage2 "_boot"
$logs = Join-Path $stage2 "_logs"
New-Item -ItemType Directory -Force -Path $boot | Out-Null
New-Item -ItemType Directory -Force -Path $logs | Out-Null

$targets = [ordered]@{
    "CAL-lux4"   = "C:\dev\music-app\builder\scratch\graph-lux4.bin"
    "CAL-served" = "C:\dev\music-app\builder\scratch\graph-msw-tu50.bin"
    "LBA-A1"     = "C:\unsung-fast\lbd-artifacts\LBA-A1-bare.bin"
    "LBA-A3"     = "C:\unsung-fast\lbd-artifacts\LBA-A3-bare.bin"
}
foreach ($arm in @("A2", "A4", "A5", "A6", "A7", "A8", "A9")) {
    $path = "C:\unsung-fast\lbd-artifacts\LBA-$arm.bin"
    if (Test-Path $path) { $targets["LBA-$arm"] = $path }
}

Set-Location $here
foreach ($label in $targets.Keys) {
    $artifact = $targets[$label]
    foreach ($r in 1, 2, 3) {
        $out = Join-Path $boot ($label + "_r" + $r + ".json")
        & uv run python -u analysis/2026-09-14-lbd-s4-stage2/s4_boot_rss.py `
            --artifact $artifact --label $label --repeat $r --out $out
        if ($LASTEXITCODE -ne 0) {
            Write-Output "=== boot RSS $label r$r FAILED rc=$LASTEXITCODE ==="
            exit $LASTEXITCODE
        }
    }
}
Write-Output "=== boot RSS complete $(Get-Date -Format o) ==="
