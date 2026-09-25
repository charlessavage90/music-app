"""#142: d0 query cost on the production container, stage-2 pair set, via the front door.

Paced at one request per 1.3 s start-to-start (under Cloudflare's 10 / 10 s). A 429 has no
server-side timing and self-excludes. Server-side timing is read afterwards from CloudWatch
(`duration_ms`, which brackets exactly `find_journey`, the quantity stage 2 timed locally).
"""
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

PAIRS, OUT = sys.argv[1], sys.argv[2]
URL = "https://unsung.fm/api/path"
pairs = [l.split("\t") for l in open(PAIRS).read().splitlines() if l.strip()]

with open(OUT, "w") as f:
    f.write(json.dumps({"start_utc": datetime.now(timezone.utc).isoformat(), "n": len(pairs)}) + "\n")
    for i, (a, b) in enumerate(pairs):
        t0 = time.perf_counter()
        body = json.dumps({"sources": [a, b], "exclude": []}).encode()
        req = urllib.request.Request(URL, data=body, headers={"content-type": "application/json",
                                                         # Cloudflare 1010-blocks Python-urllib's default UA
                                                         "User-Agent": "artistpath-p95-probe/1.0 (#142)"})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                status = r.status
                n = len(json.load(r).get("artists", []))
        except urllib.error.HTTPError as e:
            status, n = e.code, None
        client_ms = (time.perf_counter() - t0) * 1000
        f.write(json.dumps({"i": i, "a": a, "b": b, "status": status, "artists": n, "client_ms": round(client_ms, 1)}) + "\n")
        f.flush()
        print(i, status, round(client_ms), flush=True)
        time.sleep(max(0.0, 1.3 - (time.perf_counter() - t0)))
    f.write(json.dumps({"end_utc": datetime.now(timezone.utc).isoformat()}) + "\n")
