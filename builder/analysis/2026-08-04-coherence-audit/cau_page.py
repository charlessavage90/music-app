"""CAU- serving: the audit page, with judgements written to disk as they are saved.

Verdicts survive a restart (reloaded from disk), which the GBL- run proved matters
across sittings. /status is the authority on completeness -- a direct file read timed
against the owner's actions is not (GBL- run log §6).
"""
from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

from cau_common import VERDICTS, in_dir

PORT = 8766          # deliberately not GBL-'s 8765


def build_server(page_data: dict, verdict_file, port: int = PORT):
    state: dict = {"slots": {}, "journey_notes": {}}
    if verdict_file.exists():
        state.update(json.loads(verdict_file.read_text("utf-8")))
        state.setdefault("slots", {})
        state.setdefault("journey_notes", {})

    slots = []
    for j in page_data["journeys"]:
        for i, a in enumerate(j["artists"]):
            if a["role"] == "interior":
                slots.append(f"{j['id']}#{i}")

    def save():
        tmp = verdict_file.with_suffix(".tmp")
        tmp.write_text(json.dumps(state, indent=2, ensure_ascii=False),
                       encoding="utf-8")
        tmp.replace(verdict_file)

    def missing():
        out = [s for s in slots if state["slots"].get(s) is None]
        out += [f"{j['id']}:note" for j in page_data["journeys"]
                if j["id"] not in state["journey_notes"]]
        return out

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *a):
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
                html = in_dir("cau_page.html").read_text("utf-8")
                html = html.replace("/*DATA*/", json.dumps(page_data,
                                                           ensure_ascii=False))
                html = html.replace("/*SAVED*/", json.dumps(state,
                                                            ensure_ascii=False))
                self._send(200, html, "text/html")
            elif self.path == "/status":
                m = missing()
                self._send(200, json.dumps({"complete": not m,
                                            "missing_count": len(m),
                                            "missing": m}))
            else:
                self._send(404, "{}")

        def do_POST(self):
            n = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(n) or b"{}")
            if self.path == "/judge":
                if body.get("verdict") not in VERDICTS:
                    return self._send(400, f"bad verdict {body.get('verdict')!r}")
                if body.get("slot") not in slots:
                    return self._send(400, f"unknown slot {body.get('slot')!r}")
                state["slots"][body["slot"]] = {
                    "verdict": body["verdict"],
                    "looked_up": bool(body.get("looked_up")),
                    "note": body.get("note", ""),
                }
                save()
                return self._send(200, "{}")
            if self.path == "/journey_note":
                state["journey_notes"][body["journey"]] = body.get("note", "")
                save()
                return self._send(200, "{}")
            self._send(404, "{}")

    return HTTPServer(("127.0.0.1", port), Handler)


def main() -> int:
    page = json.loads(in_dir("cau_page_data.json").read_text("utf-8"))
    srv = build_server(page, in_dir("cau_judgements.json"))
    print(f"serving http://127.0.0.1:{PORT}/  (ctrl-c to stop)", flush=True)
    srv.serve_forever()
    return 0


if __name__ == "__main__":
    sys.exit(main())
