"""Write `lal_maps.json` — the listen's map pin — from the two artifacts' sidecars (`LBA-AM6-1`).

*"Both shas are read from the sidecars by script into the listen's map pin, never transcribed."*
Each sha is taken from the sidecar AND recomputed from the bytes; a disagreement refuses. The
production twin's sha is pinned beside the served map's so generation's routing-identity gate
checks the artifact the deploy actually serves.

    cd builder && UV_LINK_MODE=copy uv run python -u analysis/2026-09-22-lba-a6-blind-listen/lal_pin_maps.py
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lal_common import CANDIDATE, MAPS_PIN, PRODUCTION, SERVED, sha256_of, sidecar  # noqa: E402


def pin(path: Path) -> dict:
    recorded = sidecar(path)["sha256"]
    actual = sha256_of(path)
    if actual != recorded:
        raise SystemExit(f"REFUSING: {path.name} bytes {actual} != sidecar {recorded}")
    return {"path": str(path), "sha256": recorded}


def main() -> int:
    doc = {
        "_note": ("LBA-AM6-1. Incumbent = today's served map (ApiConfig.graph_path's default); "
                  "challenger = the LBA-A6 candidate. Written by lal_pin_maps.py from the sidecars, "
                  "each checked against its bytes. Roles only; the left/right assignment is sealed "
                  "at generation."),
        "incumbent": pin(SERVED),
        "challenger": pin(CANDIDATE),
        "production_twin": pin(PRODUCTION),
        "written_utc": datetime.now(timezone.utc).isoformat(),
    }
    MAPS_PIN.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    for k in ("incumbent", "challenger", "production_twin"):
        print(f"[pin] {k}: {Path(doc[k]['path']).name} {doc[k]['sha256']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
