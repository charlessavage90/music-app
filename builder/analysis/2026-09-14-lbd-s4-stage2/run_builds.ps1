# LBA- stage 2, step 3 -- build the seven emitted cells, ONE PROCESS PER BUILD.
#
# ORDER: ascending archive neighbour rows, per LBA-AM2(c) and the stage-1 README's table:
#   A2 (8,936,730) -> A4 -> A5 -> A6 -> A7 -> A8 -> A9 (52,254,182)
# The first build is unevaluable by LBA-G2 and proceeds unconditionally (LBA-AM2(b)); it is
# bracketed by the two reused archives, both of which built on this machine.
#
# ONE PROCESS PER BUILD is not a convention here -- PeakWorkingSetSize never falls, so a second
# build in one process would read the first one's peak. `instrumented_build` refuses rather than
# trusting this script.
#
# A cell LBA-G2 stops returns 0 and writes an "unbuilt for a resource reason" record: that is a
# resource fact, not a failure, and the chain CONTINUES to the next cell. Only a real error
# (non-zero exit) stops the chain.
#
# ASCII ONLY -- Windows PowerShell 5.1 reads a BOM-less UTF-8 .ps1 as ANSI.
$ErrorActionPreference = "Continue"
$env:UV_LINK_MODE = "copy"
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUNBUFFERED = "1"

$here = "C:\dev\music-app\builder"
$logs = "C:\dev\music-app\builder\analysis\2026-09-14-lbd-s4-stage2\_logs"
New-Item -ItemType Directory -Force -Path $logs | Out-Null

Set-Location $here
foreach ($arm in @("A2", "A4", "A5", "A6", "A7", "A8", "A9")) {
    Write-Output "=== build LBA-$arm start $(Get-Date -Format o) ==="
    $log = Join-Path $logs ("build_" + $arm + ".log")
    & uv run python -u analysis/2026-09-14-lbd-s4-stage2/s4_build.py --arm $arm *>&1 |
        Tee-Object -FilePath $log
    $rc = $LASTEXITCODE
    if ($rc -ne 0) {
        Write-Output "=== build LBA-$arm FAILED rc=$rc -- chain stops here ==="
        exit $rc
    }
    Write-Output "=== build LBA-$arm done $(Get-Date -Format o) ==="
}
Write-Output "=== build chain complete $(Get-Date -Format o) ==="
