# LBA-M1 -- bare copies, then boot memory and the metadata_ratio calibration.
# ONE LOAD PER PROCESS, three repeats each.
#
# PeakWorkingSetSize is a whole-process high-water mark and never falls, so two loads in one
# process would give the second one the first one's peak. Every repeat is therefore its own
# process, and this script is only the loop.
#
# STEP 1 -- a BARE re-serialisation of every arm, the two reused and the seven built alike.
# require_fame=False removes FAME ONLY: deezer_ids and the three LUX-4 keys load from frozen
# sha-pinned package data rather than a fetch, so a census build carries four of the five additive
# keys, and the two reused arms' artifacts carry all five. Applying metadata_ratio to either would
# scale metadata that is already present -- double-counting the exact term the ratio measures.
# Measuring every arm bare and then scaling is the same treatment section 4 already fixes for the
# bytes half, applied to the memory half so the two are consistent.
#
# STEP 2 -- what is measured, and the two entries that are NOT arms:
#   CAL-lux4 / CAL-served  the metadata_ratio calibration pair, measured AS THEY ARE. They are
#                          identical in artist count and CSR entries and differ only in the three
#                          LUX-4 keys, which is what makes the ratio isolate the metadata term.
#                          These two are never bare-copied: the difference between them IS the
#                          measurement.
#   LBA-A1 .. LBA-A9       every arm, on its bare copy.
#
# ASCII ONLY -- Windows PowerShell 5.1 reads a BOM-less UTF-8 .ps1 as ANSI.
$ErrorActionPreference = "Continue"
$env:UV_LINK_MODE = "copy"
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUNBUFFERED = "1"

$here = "C:\dev\music-app\builder"
$stage2 = "C:\dev\music-app\builder\analysis\2026-09-14-lbd-s4-stage2"
$boot = Join-Path $stage2 "_boot"
New-Item -ItemType Directory -Force -Path $boot | Out-Null
Set-Location $here

# --- step 1: bare copies -------------------------------------------------------------------
$sources = [ordered]@{
    "LBA-A1" = "C:\unsung-fast\lbd-artifacts\LBD-A0V.bin"
    "LBA-A3" = "C:\unsung-fast\lbd-artifacts\LBD-A5V.bin"
}
foreach ($arm in @("A2", "A4", "A5", "A6", "A7", "A8", "A9")) {
    $path = "C:\unsung-fast\lbd-artifacts\LBA-$arm.bin"
    if (Test-Path $path) { $sources["LBA-$arm"] = $path }
}
foreach ($label in $sources.Keys) {
    $bare = "C:\unsung-fast\lbd-artifacts\$label-bare.bin"
    if (Test-Path $bare) { Write-Output "[bare] $label already present"; continue }
    & uv run python -u analysis/2026-09-14-lbd-s4-stage2/s4_bare_copy.py `
        --artifact $sources[$label] --label $label
    if ($LASTEXITCODE -ne 0) { Write-Output "=== bare copy $label FAILED ==="; exit $LASTEXITCODE }
}

# --- step 2: boot RSS, three repeats, one process each --------------------------------------
$targets = [ordered]@{
    "CAL-lux4"   = "C:\dev\music-app\builder\scratch\graph-lux4.bin"
    "CAL-served" = "C:\dev\music-app\builder\scratch\graph-msw-tu50.bin"
}
foreach ($label in $sources.Keys) {
    $targets[$label] = "C:\unsung-fast\lbd-artifacts\$label-bare.bin"
}

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
