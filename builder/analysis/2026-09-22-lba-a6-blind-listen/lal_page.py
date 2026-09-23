"""Serves the side-by-side page on localhost and writes every answer to disk as it is saved.

Adapted by copy from listen 2's `lbl_page.py`, with `LBA-AM6-4`'s row: `LAL-Q1` coherence, `LAL-Q2`
novelty, `LAL-Q3` pick strength per axis, `LAL-Q4` "can you tell which side is the new map" (shown
only after Q1 and Q2), the `LAL-K` known-everyone box, the clip-problem box and notes. `LBL-Q3`'s
trade-off question is DROPPED. Per pair: the collapse question and notes. Stdlib only.

    cd <tree>/builder && UV_LINK_MODE=copy uv run python analysis/2026-09-22-lba-a6-blind-listen/lal_page.py
"""
from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lal_common import AXES, DEPTHS, IDENTIFY, STRENGTHS, TOKENS, in_dir, sealed_path  # noqa: E402

PICKS = (*TOKENS, "none")
MAX_NOTE = 20_000
VERDICTS = "lal_verdicts.json"


def strength_field(question: str) -> str:
    return f"{question}_strength"


def _embed(payload: dict) -> str:
    """JSON for a <script> block; `<` escaped so a name containing `</script>` cannot end it."""
    return json.dumps(payload, ensure_ascii=False).replace("<", "\\u003c")


def row_complete(entry: dict | None) -> bool:
    """Both axes, a strength wherever an axis carries a clear pick (and none where it does not),
    `LAL-Q4`, and the two booleans."""
    if not entry or not all(entry.get(q) in PICKS for q in AXES):
        return False
    for q in AXES:
        owed, got = entry.get(q) in TOKENS, entry.get(strength_field(q))
        if (owed and got not in STRENGTHS) or (not owed and got is not None):
            return False
    if entry.get("identify") not in IDENTIFY:
        return False
    return isinstance(entry.get("known_everyone"), bool) and isinstance(entry.get("clip_blocked"), bool)


def missing_slots(state: dict, pair_keys: list[str]) -> list[str]:
    out = []
    for k in pair_keys:
        for d in DEPTHS:
            if not row_complete(state["rows"].get(k, {}).get(str(d))):
                out.append(f"{k}:d{d}")
        if k not in state["pairs"]:
            out.append(f"{k}:pair")
    return out


def apply_post(state: dict, path: str, body: dict, pair_keys: list[str]) -> None:
    """Validate and apply one save. Raises ValueError/KeyError on anything undesigned."""
    pair = body["pair"]
    if pair not in pair_keys:
        raise ValueError("unknown pair")
    if path == "/row":
        depth = str(body["depth"])
        if depth not in {str(d) for d in DEPTHS}:
            raise ValueError("bad depth")
        entry = {q: body[q] for q in AXES}
        if any(v not in PICKS for v in entry.values()):
            raise ValueError("bad pick")
        for q in AXES:
            given = body.get(strength_field(q))
            if entry[q] in TOKENS:
                if given not in STRENGTHS:
                    raise ValueError(f"{strength_field(q)} must be one of {STRENGTHS}")
            elif given is not None:
                raise ValueError(f"{strength_field(q)} is meaningless without a pick")
            entry[strength_field(q)] = given if entry[q] in TOKENS else None
        if body.get("identify") not in IDENTIFY:
            raise ValueError(f"identify must be one of {IDENTIFY}")
        entry["identify"] = body["identify"]
        for flag in ("known_everyone", "clip_blocked"):
            if not isinstance(body.get(flag, False), bool):
                raise ValueError(f"{flag} must be true or false")
            entry[flag] = body.get(flag, False)
        entry["notes"] = str(body.get("notes", ""))[:MAX_NOTE]
        state["rows"].setdefault(pair, {})[depth] = entry
    elif path == "/pair":
        state["pairs"][pair] = {"collapse": str(body.get("collapse", ""))[:MAX_NOTE],
                                "notes": str(body.get("notes", ""))[:MAX_NOTE]}
    else:
        raise KeyError(path)


def make_server(page_data: dict, clips: dict, verdict_file: Path, port: int = 8765):
    html = (Path(__file__).parent / "lal_page.html").read_text(encoding="utf-8")
    html = html.replace("__LAL_DATA__", _embed({"pairs": page_data["pairs"], "clips": clips}))
    pair_keys = [p["key"] for p in page_data["pairs"]]
    state: dict = {"rows": {}, "pairs": {}}
    if verdict_file.exists():   # resuming a split sitting keeps prior answers
        state = json.loads(verdict_file.read_text("utf-8"))
        state.setdefault("rows", {})
        state.setdefault("pairs", {})

    def save() -> None:
        tmp = verdict_file.with_suffix(".tmp")
        tmp.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
        tmp.replace(verdict_file)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def _send(self, code: int, body: str, ctype: str = "application/json") -> None:
            data = body.encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", f"{ctype}; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            if self.path == "/":
                self._send(200, html, "text/html")
            elif self.path == "/status":
                m = missing_slots(state, pair_keys)
                self._send(200, json.dumps({"complete": not m, "missing": m}))
            else:
                self._send(404, "{}")

        def do_POST(self):
            n = int(self.headers.get("Content-Length", 0))
            if n > 4 * MAX_NOTE:
                self._send(413, '{"error": "too large"}')
                return
            try:
                apply_post(state, self.path, json.loads(self.rfile.read(n)), pair_keys)
            except KeyError:
                self._send(404, "{}")
                return
            except (ValueError, TypeError, json.JSONDecodeError) as e:
                self._send(400, json.dumps({"error": str(e)}))
                return
            save()
            self._send(200, '{"ok": true}')

    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


def main() -> int:
    page_data = json.loads(in_dir("lal_page_data.json").read_text("utf-8"))
    clips = json.loads(sealed_path("lal_clips.json").read_text("utf-8"))
    srv = make_server(page_data, clips, verdict_file=in_dir(VERDICTS))
    print(f"serving http://127.0.0.1:{srv.server_address[1]}/ -- Ctrl+C to stop", flush=True)
    srv.serve_forever()
    return 0


if __name__ == "__main__":
    sys.exit(main())
