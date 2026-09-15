# Machine-state timeline for the stage-2 build chain. Touches no build script and races nothing:
# it aligns with each build's own start/finish timestamps in s4_build_<arm>.json after the fact.
# Exists so "was the machine quiet for this build" is answerable from the RECORD rather than from
# anyone's memory of the evening.
$out = "C:\dev\music-app\builder\analysis\2026-09-14-lbd-s4-stage2\_logs\machine_state.tsv"
"utc`tfree_mb`ttotal_mb" | Out-File -FilePath $out -Encoding utf8
while ($true) {
    $os = Get-CimInstance Win32_OperatingSystem
    $line = "{0}`t{1}`t{2}" -f (Get-Date).ToUniversalTime().ToString("o"), [math]::Round($os.FreePhysicalMemory/1KB), [math]::Round($os.TotalVisibleMemorySize/1KB)
    $line | Out-File -FilePath $out -Encoding utf8 -Append
    Start-Sleep -Seconds 20
}
