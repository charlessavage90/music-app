"""Preserve the live app's CloudWatch telemetry, tagged by graph era.

WHY THIS EXISTS. App Runner log groups carry 90-day retention (set at
`infra/README.md` §5a, confirmed 2026-08-06). The PRE-adoption corpus is
therefore fixed, finite and SHRINKING — it can only get smaller as it ages out,
with the earliest events (2026-07-26) expiring around 2026-10-24. The
post-adoption corpus grows. That asymmetry is the whole argument for pulling:
this is preservation, not analysis.

**NO METRIC IS COMPUTED HERE, DELIBERATELY.** `telemetry.py` records facts and
not metrics on purpose (DEP-7: choosing which metric production computes is a
scoring decision). Choosing one *after* seeing both eras is exactly the fishing
the pre-registration discipline exists to prevent. This script extracts and
tags; it does not aggregate, and a future comparison names its metric first.

ERA IS DETERMINED BY LOG STREAM, NEVER BY TIMESTAMP. App Runner rolls
deployments, so the outgoing and incoming instances SERVE CONCURRENTLY — on
2026-08-06 the new instance began at 09:37:22 while the old one kept answering
until 09:46:13, a ~9-minute window in which a timestamp filter attributes
old-graph journeys to the new graph. Each instance is its own stream and each
stream ran exactly one artifact, so the stream is unambiguous where the clock is
not.

The mapping below was VERIFIED rather than inferred from timing: a journey run
against a `/health` that had already reported the new sha appears only in
`2e9ff5f0…`.
"""

from __future__ import annotations

import gzip
import json
import subprocess
import sys
from pathlib import Path

SERVICE_ID = "40e4a1cf20414bce96a7a46b5e62c3a6"
GROUP = f"/aws/apprunner/artistpath-api/{SERVICE_ID}/application"

# The adoption. Recorded for provenance and for filtering downstream; NOT used
# to assign era — see the module docstring.
DEPLOY_COMMIT = "a06ab58"
DEPLOY_IMAGE = "artistpath-api:a06ab58"
NEW_GRAPH_SHA = "43dd82bb3771691ed778c1f2a3a079cdad0bd75636b2bedb1c754c8a2be79cc8"
OLD_GRAPH = "graph-t15-tiebreakfix.bin"
NEW_GRAPH = "graph-msw-tu50.bin"

STREAM_ERA = {
    "instance/e88655f1fab04c789203c7a0cb6b0130": "pre_msw",
    "instance/ab304fc6b8c640798c839f271ab840db": "pre_msw",
    "instance/58b2c316ea4344c087a049563f0a1a56": "pre_msw",
    "instance/2e9ff5f0c20344bd9f395a259b218bbe": "post_msw",
}

OUT_DIR = Path(__file__).parent


def _aws(*args: str) -> dict:
    """Run the AWS CLI and parse JSON.

    MSYS_NO_PATHCONV is set by the caller's environment on Git Bash; passing the
    log-group name through a shell there rewrites `/aws/apprunner/...` into a
    Windows path and the API rejects it naming the parameter but not the cause
    (execution log §6). subprocess with a list argv avoids the shell entirely,
    which is why it is used rather than a formatted command string.
    """
    proc = subprocess.run(
        ["aws", *args], capture_output=True, text=True, encoding="utf-8"
    )
    if proc.returncode != 0:
        sys.exit(f"aws {' '.join(args[:3])} failed:\n{proc.stderr.strip()}")
    return json.loads(proc.stdout)


def pull_stream(stream: str) -> list[dict]:
    """Every event in one stream, following the forward token to exhaustion."""
    events: list[dict] = []
    token: str | None = None
    while True:
        args = [
            "logs", "get-log-events",
            "--log-group-name", GROUP,
            "--log-stream-name", stream,
            "--start-from-head",
            "--limit", "10000",
        ]
        if token:
            args += ["--next-token", token]
        page = _aws(*args)
        batch = page.get("events", [])
        events.extend(batch)
        nxt = page.get("nextForwardToken")
        # TERMINATE ONLY ON AN UNCHANGED TOKEN, NEVER ON AN EMPTY PAGE.
        # get-log-events can return zero events with a valid forward token while
        # more data remains, so `not batch` is NOT end-of-stream. An earlier
        # version of this script broke on it and silently dropped 38 of the 271
        # pre-adoption `path` events — a ~14% undercount that looked like a
        # complete pull, and was caught only by cross-checking the totals
        # against Log Insights. Preservation that silently truncates is worse
        # than no preservation, because the manifest asserts a count.
        if nxt == token:
            break
        token = nxt
    return events


def main() -> int:
    records: list[dict] = []
    per_stream: dict[str, int] = {}

    for stream, era in STREAM_ERA.items():
        raw = pull_stream(stream)
        per_stream[stream] = len(raw)
        print(f"  {stream[-12:]}  {era:9}  {len(raw):5} events", flush=True)
        for e in raw:
            rec = {
                "era": era,
                "stream": stream,
                "timestamp": e["timestamp"],
                "raw": e["message"].rstrip("\n"),
            }
            # Telemetry lines are single-line JSON; App Runner's own operational
            # noise is not. Parse opportunistically and keep the raw line either
            # way, so nothing is discarded on a parse failure.
            try:
                parsed = json.loads(rec["raw"])
                if isinstance(parsed, dict) and "event" in parsed:
                    rec["telemetry"] = parsed
            except (ValueError, TypeError):
                pass
            records.append(rec)

    records.sort(key=lambda r: r["timestamp"])

    # TWO outputs, deliberately. Only ~1% of what App Runner ships to CloudWatch
    # is telemetry; the rest is health-check and platform noise. The parsed
    # events go in a readable file small enough to grep and diff in git, and the
    # complete corpus goes beside it gzipped, so nothing is discarded and the
    # 90-day expiry costs nothing. Uncompressed the full corpus is ~17 MB, which
    # is not worth putting in git history forever; gzipped it is under 1 MB.
    out = OUT_DIR / "telemetry_events.jsonl"
    with out.open("w", encoding="utf-8") as fh:
        for r in records:
            if "telemetry" in r:
                fh.write(json.dumps(r, separators=(",", ":")) + "\n")

    raw_out = OUT_DIR / "raw_all_events.jsonl.gz"
    with gzip.open(raw_out, "wt", encoding="utf-8", compresslevel=9) as fh:
        for r in records:
            fh.write(json.dumps(r, separators=(",", ":")) + "\n")

    def count(era: str, kind: str | None = None) -> int:
        return sum(
            1
            for r in records
            if r["era"] == era
            and (kind is None or r.get("telemetry", {}).get("event") == kind)
        )

    manifest = {
        "pulled_at_utc": _aws("logs", "describe-log-groups",
                              "--log-group-name-prefix", GROUP,
                              "--query", "logGroups[0].creationTime") and None,
        "log_group": GROUP,
        "retention_days": 90,
        "purpose": "preservation of the pre-adoption telemetry corpus; no metric computed",
        "era_assigned_by": "log stream, never timestamp — the rolling deploy overlapped",
        "deploy": {
            "commit": DEPLOY_COMMIT,
            "image": DEPLOY_IMAGE,
            "old_graph": OLD_GRAPH,
            "new_graph": NEW_GRAPH,
            "new_graph_sha256": NEW_GRAPH_SHA,
        },
        "streams": {s: {"era": e, "events": per_stream[s]} for s, e in STREAM_ERA.items()},
        "counts": {
            "total_events": len(records),
            "pre_msw": {
                "all": count("pre_msw"),
                "path": count("pre_msw", "path"),
                "clip": count("pre_msw", "clip"),
            },
            "post_msw": {
                "all": count("post_msw"),
                "path": count("post_msw", "path"),
                "clip": count("post_msw", "clip"),
            },
        },
        "caveats": [
            "The pre_msw path corpus is heavily synthetic: one journey at each "
            "consecutive bypass_depth from 26 to 46, plus clusters at exactly 50 "
            "and 100, are a script walking one press at a time rather than use.",
            "193 of the pre_msw path events fall on 2026-07-28 alone.",
            "Some post_msw events are a session's own deploy verification "
            "(a Radiohead -> Miles Davis journey pressed five times), not owner use.",
            "The two eras differ in MORE than the graph: the owner's usage pattern "
            "changes deliberately after adoption (the queued test asks for ten or "
            "more 'known' presses), and the deploy moved several knobs at once. "
            "A before/after difference is NOT attributable to any one of them.",
        ],
    }
    manifest.pop("pulled_at_utc")

    (OUT_DIR / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )

    tel = sum(1 for r in records if "telemetry" in r)
    print(f"\nwrote {out.name}: {tel} telemetry events")
    print(f"wrote {raw_out.name}: {len(records)} events (complete corpus)")
    print(json.dumps(manifest["counts"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
