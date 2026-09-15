# LBA- stage 2, step 2 -- emit the seven unbuilt cells, one process each.
#
# ORDER: A4 FIRST, and deliberately. The existing `A0` archive is exactly LBA-A4 (threshold 10,
# population P) and its committed counts are stage 1's figures for that cell, so re-emitting it
# proves this wrapper against a committed record before it is used on any cell nobody has emitted
# before. The rest follow in ascending archive-neighbour-row order.
#
# RUN ALONE and SEQUENTIALLY: DuckDB, per the task 6-7 log's access-violation trap.
#
# ASCII ONLY. Windows PowerShell 5.1 reads a BOM-less UTF-8 .ps1 as ANSI, and a multi-byte
# character in a comment breaks the parse of a string many lines later. Cost one launch here.
$ErrorActionPreference = "Continue"
$env:UV_LINK_MODE = "copy"
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUNBUFFERED = "1"

$here = "C:\dev\music-app\builder"
$logs = "C:\dev\music-app\builder\analysis\2026-09-14-lbd-s4-stage2\_logs"
New-Item -ItemType Directory -Force -Path $logs | Out-Null

Set-Location $here
foreach ($arm in @("A4", "A2", "A5", "A6", "A7", "A8", "A9")) {
    $stamp = Get-Date -Format o
    Write-Output "=== emit LBA-$arm start $stamp ==="
    $log = Join-Path $logs ("emit_" + $arm + ".log")
    & uv run --with duckdb python -u analysis/2026-09-14-lbd-s4-stage2/s4_emit.py --arm $arm *>&1 |
        Tee-Object -FilePath $log
    $rc = $LASTEXITCODE
    if ($rc -ne 0) {
        Write-Output "=== emit LBA-$arm FAILED rc=$rc -- chain stops here ==="
        exit $rc
    }
    Write-Output "=== emit LBA-$arm done $(Get-Date -Format o) ==="
}
Write-Output "=== all seven emits complete $(Get-Date -Format o) ==="
