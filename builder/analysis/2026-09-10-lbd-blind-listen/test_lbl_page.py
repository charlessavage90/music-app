import json
import threading
import urllib.request
from pathlib import Path

import pytest

from lbl_common import DEPTHS
from lbl_page import apply_post, make_server, missing_slots

HTML = (Path(__file__).parent / "lbl_page.html").read_text(encoding="utf-8")
KEYS = ["a|b", "c|d"]

# LBD-AM5-5's frozen wordings. If the page drifts from the amendment, this goes red before a run.
FROZEN = (
    "At this point, which side holds together better as a journey — each step a sensible next listen?",
    "At this point, which side gives you more artists that are new to you?",
    "a clip problem stopped me judging this row",
    "Did either side collapse into a random walk into obscurity? If so, which and where?",
)


@pytest.mark.parametrize("wording", FROZEN)
def test_the_page_carries_each_frozen_wording_verbatim(wording):
    assert wording in HTML


def test_the_page_never_assigns_innerhtml():
    # The file's header comment names the rule; what must never appear is the property in use.
    assert ".innerHTML" not in HTML


def fresh():
    return {"rows": {}, "pairs": {}}


def test_a_row_needs_both_questions_to_count():
    s = fresh()
    apply_post(s, "/row", {"pair": "a|b", "depth": "0", "q1": "L", "q2": "none"}, KEYS)
    assert "a|b:d0" not in missing_slots(s, KEYS)
    s["rows"]["a|b"]["10"] = {"q1": "L"}
    assert "a|b:d10" in missing_slots(s, KEYS)


def test_status_lists_every_row_and_pair_until_saved():
    assert len(missing_slots(fresh(), KEYS)) == len(KEYS) * (len(DEPTHS) + 1)


@pytest.mark.parametrize("body", [
    {"pair": "zz", "depth": "0", "q1": "L", "q2": "L"},
    {"pair": "a|b", "depth": "5", "q1": "L", "q2": "L"},
    {"pair": "a|b", "depth": "0", "q1": "left", "q2": "L"},
    {"pair": "a|b", "depth": "0", "q1": "L", "q2": "L", "clip_blocked": "yes"},
])
def test_undesigned_rows_are_refused(body):
    with pytest.raises(ValueError):
        apply_post(fresh(), "/row", body, KEYS)


def test_an_unknown_endpoint_is_refused():
    with pytest.raises(KeyError):
        apply_post(fresh(), "/verdict", {"pair": "a|b"}, KEYS)


def _post(port, path, body):
    req = urllib.request.Request(f"http://127.0.0.1:{port}{path}", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req) as r:
        return r.status


def _get(port, path):
    with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}") as r:
        return r.read().decode("utf-8")


def test_answers_are_written_to_disk_and_survive_a_restart(tmp_path):
    page = {"pairs": [{"key": k, "a": "A", "b": "B", "rows": []} for k in KEYS]}
    verdicts = tmp_path / "v.json"
    srv = make_server(page, {}, verdicts, port=0)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    port = srv.server_address[1]
    assert "<script>" in _get(port, "/")
    assert _post(port, "/row", {"pair": "a|b", "depth": 10, "q1": "R", "q2": "none", "clip_blocked": True}) == 200
    srv.shutdown()
    saved = json.loads(verdicts.read_text("utf-8"))
    assert saved["rows"]["a|b"]["10"] == {"q1": "R", "q2": "none", "clip_blocked": True, "notes": ""}

    srv2 = make_server(page, {}, verdicts, port=0)
    threading.Thread(target=srv2.serve_forever, daemon=True).start()
    status = json.loads(_get(srv2.server_address[1], "/status"))
    srv2.shutdown()
    assert "a|b:d10" not in status["missing"] and not status["complete"]


def test_a_name_containing_a_script_close_cannot_end_the_block(tmp_path):
    page = {"pairs": [{"key": "a|b", "a": "</script><b>", "b": "B", "rows": []}]}
    srv = make_server(page, {}, tmp_path / "v.json", port=0)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    body = _get(srv.server_address[1], "/")
    srv.shutdown()
    assert "</script><b>" not in body
