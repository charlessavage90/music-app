# Wait for the emit chain, then start the build chain -- both detached, neither harness-tracked.
#
# WHY THE PHASES ARE SEQUENCED AND NOT OVERLAPPED, and it is a measurement reason rather than a
# tidiness one. The first build's peak RSS is the SINGLE POINT every later LBA-G2 projection
# extrapolates from (LBA-AM2(d): one point -> proportional through the origin). Windows trims a
# process's working set under memory pressure, so a peak measured while the A9 emit holds most of
# a 32 GB machine would read LOWER than the same build on a quiet machine -- and a low first point
# makes every subsequent projection OPTIMISTIC, which is the direction that admits a cell the gate
# should have stopped. So the builds wait for a quiet machine.
#
# ASCII ONLY -- Windows PowerShell 5.1 reads a BOM-less UTF-8 .ps1 as ANSI.
$ErrorActionPreference = "Continue"
$stage2 = "C:\dev\music-app\builder\analysis\2026-09-14-lbd-s4-stage2"
$chainLog = Join-Path $stage2 "_logs\emit_chain.log"

while ($true) {
    $text = Get-Content $chainLog -Raw -ErrorAction SilentlyContinue
    if ($text -match "all seven emits complete") {
        Write-Output "=== emits complete, starting builds $(Get-Date -Format o) ==="
        break
    }
    if ($text -match "FAILED") {
        Write-Output "=== emit chain FAILED -- builds NOT started $(Get-Date -Format o) ==="
        exit 1
    }
    Start-Sleep -Seconds 20
}

# Let the machine settle before the first instrumented build: the emit process has just exited and
# its pages are still being reclaimed.
Start-Sleep -Seconds 60
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $stage2 "run_builds.ps1")
exit $LASTEXITCODE
