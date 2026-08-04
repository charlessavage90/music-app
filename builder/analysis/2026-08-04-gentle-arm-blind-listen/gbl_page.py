"""Serves the side-by-side page on localhost and writes verdicts to disk --
the owner's §3.9 improvement request. Stdlib only; throwaway."""
from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from gbl_common import DEPTHS, TOKENS, in_dir, sealed_path

PICKS = (*TOKENS, "none")


def _embed(payload: dict) -> str:
    """JSON for a <script> block. `<` is escaped because an artist name
    containing `</script>` would otherwise end the block and blank the page --
    and the names come from MusicBrainz, not from us."""
    return json.dumps(payload, ensure_ascii=False).replace("<", "\\u003c")


def make_server(page_data: dict, clips: dict, verdict_file: Path, port: int = 8765):
    html = (Path(__file__).parent / "gbl_page.html").read_text(encoding="utf-8")
    html = html.replace("__GBL_DATA__",
                        _embed({"pairs": page_data["pairs"], "clips": clips}))
    valid_pairs = [p["key"] for p in page_data["pairs"]]
    state: dict = {"rows": {}, "claims": {}}
    if verdict_file.exists():   # resuming a split sitting keeps prior verdicts
        state = json.loads(verdict_file.read_text("utf-8"))
        state.setdefault("rows", {})
        state.setdefault("claims", {})

    def save():
        tmp = verdict_file.with_suffix(".tmp")
        tmp.write_text(json.dumps(state, indent=2, ensure_ascii=False),
                       encoding="utf-8")
        tmp.replace(verdict_file)

    def missing():
        out = []
        for k in valid_pairs:          # page order, so the list reads top-down
            for d in DEPTHS:
                if state["rows"].get(k, {}).get(str(d)) is None:
                    out.append(f"{k}:d{d}")
            if k not in state["claims"]:
                out.append(f"{k}:claims")
        return out

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *a):   # quiet
            pass

        def _send(self, code, body, ctype="application/json"):
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
                m = missing()
                self._send(200, json.dumps({"complete": not m, "missing": m}))
            else:
                self._send(404, "{}")

        def do_POST(self):
            n = int(self.headers.get("Content-Length", 0))
            try:
                body = json.loads(self.rfile.read(n))
                pair = body["pair"]
                if pair not in valid_pairs:
                    raise ValueError("unknown pair")
                if self.path == "/verdict":
                    if (str(body["depth"]) not in {str(d) for d in DEPTHS}
                            or body["pick"] not in PICKS):
                        raise ValueError("bad row")
                    state["rows"].setdefault(pair, {})[str(body["depth"])] = body["pick"]
                elif self.path == "/claims":
                    if body["q1"] not in PICKS or body["q2"] not in PICKS:
                        raise ValueError("bad claims")
                    state["claims"][pair] = {
                        "q1": body["q1"], "q2": body["q2"],
                        "q2_collapse": str(body.get("q2_collapse", "")),
                        "notes": str(body.get("notes", ""))}
                else:
                    self._send(404, "{}")
                    return
                save()
                self._send(200, '{"ok": true}')
            except (KeyError, ValueError, json.JSONDecodeError) as e:
                self._send(400, json.dumps({"error": str(e)}))

    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


def main() -> int:
    page_data = json.loads(in_dir("gbl_page_data.json").read_text("utf-8"))
    clips = json.loads(sealed_path("gbl_clips.json").read_text("utf-8"))
    srv = make_server(page_data, clips, verdict_file=in_dir("gbl_verdicts.json"))
    print(f"serving http://127.0.0.1:{srv.server_address[1]}/ -- Ctrl+C to stop",
          flush=True)
    srv.serve_forever()
    return 0


if __name__ == "__main__":
    sys.exit(main())
