"""Serves the side-by-side page on localhost and writes every answer to disk as it is saved.

`GBL-`'s `gbl_page.py` shape, with `LBD-AM5-5`'s changes: two questions per row (`LBL-Q1`
coherence, `LBL-Q2` novelty), a per-row clip-problem box, and a per-pair collapse note. Stdlib only.

    cd <worktree>/builder && UV_LINK_MODE=copy uv run python \\
      analysis/2026-09-10-lbd-blind-listen/lbl_page.py --listen 1
"""
from __future__ import annotations

import argparse
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from lbl_common import (
    AXES,
    DEPTHS,
    LISTENS,
    ROW_EXTRAS_BY_LISTEN,
    STRENGTHS,
    TOKENS,
    TRADEOFF,
    in_dir,
    sealed_path,
)

PICKS = (*TOKENS, "none")
MAX_NOTE = 20_000


def strength_field(question: str) -> str:
    """`LBL-Q4` is asked per axis, so each axis keeps its own strength field."""
    return f"{question}_strength"


def _embed(payload: dict) -> str:
    """JSON for a <script> block; `<` escaped so a name containing `</script>` cannot end it."""
    return json.dumps(payload, ensure_ascii=False).replace("<", "\\u003c")


def row_complete(entry: dict | None, extras: tuple = ()) -> bool:
    """Both axes answered, plus whatever `extras` this listen asks for.

    `extras` defaults to empty, which is listen 1 exactly as it ran. A strength is owed only where
    the axis carries a clear pick: there is nothing to rate about *no preference*.
    """
    if not entry or not all(entry.get(q) in PICKS for q in AXES):
        return False
    if "tradeoff" in extras and entry.get("tradeoff") not in TRADEOFF:
        return False
    if "strength" in extras:
        for q in AXES:
            owed = entry.get(q) in TOKENS
            got = entry.get(strength_field(q))
            if owed and got not in STRENGTHS:
                return False
            if not owed and got is not None:
                return False
    return True


def missing_slots(state: dict, pair_keys: list[str], extras: tuple = ()) -> list[str]:
    out = []
    for k in pair_keys:
        for d in DEPTHS:
            if not row_complete(state["rows"].get(k, {}).get(str(d)), extras):
                out.append(f"{k}:d{d}")
        if k not in state["pairs"]:
            out.append(f"{k}:pair")
    return out


def apply_post(state: dict, path: str, body: dict, pair_keys: list[str], extras: tuple = ()) -> None:
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
        if not isinstance(body.get("clip_blocked", False), bool):
            raise ValueError("clip_blocked must be true or false")
        if "tradeoff" in extras:
            if body.get("tradeoff") not in TRADEOFF:
                raise ValueError(f"tradeoff must be one of {TRADEOFF}")
            entry["tradeoff"] = body["tradeoff"]
        if "strength" in extras:
            for q in AXES:
                given = body.get(strength_field(q))
                if entry[q] in TOKENS:
                    if given not in STRENGTHS:
                        raise ValueError(f"{strength_field(q)} must be one of {STRENGTHS}")
                    entry[strength_field(q)] = given
                else:
                    if given is not None:
                        raise ValueError(f"{strength_field(q)} is meaningless without a pick")
                    entry[strength_field(q)] = None
        entry["clip_blocked"] = body.get("clip_blocked", False)
        entry["notes"] = str(body.get("notes", ""))[:MAX_NOTE]
        state["rows"].setdefault(pair, {})[depth] = entry
    elif path == "/pair":
        state["pairs"][pair] = {"collapse": str(body.get("collapse", ""))[:MAX_NOTE],
                                "notes": str(body.get("notes", ""))[:MAX_NOTE]}
    else:
        raise KeyError(path)


def make_server(page_data: dict, clips: dict, verdict_file: Path, port: int = 8765,
                extras: tuple = ()):
    html = (Path(__file__).parent / "lbl_page.html").read_text(encoding="utf-8")
    html = html.replace("__LBL_DATA__", _embed({"pairs": page_data["pairs"], "clips": clips,
                                                "extras": list(extras)}))
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
                m = missing_slots(state, pair_keys, extras)
                self._send(200, json.dumps({"complete": not m, "missing": m}))
            else:
                self._send(404, "{}")

        def do_POST(self):
            n = int(self.headers.get("Content-Length", 0))
            if n > 4 * MAX_NOTE:
                self._send(413, '{"error": "too large"}')
                return
            try:
                apply_post(state, self.path, json.loads(self.rfile.read(n)), pair_keys, extras)
            except KeyError:
                self._send(404, "{}")
                return
            except (ValueError, TypeError, json.JSONDecodeError) as e:
                self._send(400, json.dumps({"error": str(e)}))
                return
            save()
            self._send(200, '{"ok": true}')

    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--listen", type=int, required=True, choices=LISTENS)
    args = ap.parse_args(argv)
    page_data = json.loads(in_dir(f"lbl_listen{args.listen}_page_data.json").read_text("utf-8"))
    clips = json.loads(sealed_path(f"lbl_listen{args.listen}_clips.json").read_text("utf-8"))
    srv = make_server(page_data, clips, verdict_file=in_dir(f"lbl_listen{args.listen}_verdicts.json"),
                      extras=ROW_EXTRAS_BY_LISTEN[args.listen])
    print(f"serving http://127.0.0.1:{srv.server_address[1]}/ -- Ctrl+C to stop", flush=True)
    srv.serve_forever()
    return 0


if __name__ == "__main__":
    sys.exit(main())
