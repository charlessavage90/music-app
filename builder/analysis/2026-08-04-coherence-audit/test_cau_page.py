import json
import threading
import urllib.request

import pytest

from cau_page import build_server


PAGE = {"journeys": [{"id": "J", "artists": [
    {"mbid": "a", "name": "A", "role": "endpoint"},
    {"mbid": "b", "name": "B", "role": "interior"},
    {"mbid": "c", "name": "C", "role": "interior"},
    {"mbid": "d", "name": "D", "role": "endpoint"}]}]}


def serve(tmp_path, port):
    f = tmp_path / "cau_judgements.json"
    srv = build_server(PAGE, f, port=port)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    return srv, f


def get(port, path):
    with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}") as r:
        return r.status, r.read().decode("utf-8")


def post(port, path, body):
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}", method="POST",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code


def test_status_lists_missing_slots_and_the_journey_note(tmp_path):
    srv, _ = serve(tmp_path, 8791)
    try:
        _, body = get(8791, "/status")
        d = json.loads(body)
        assert d["complete"] is False
        assert set(d["missing"]) == {"J#1", "J#2", "J:note"}
    finally:
        srv.shutdown()


def test_a_bad_verdict_is_refused(tmp_path):
    srv, _ = serve(tmp_path, 8792)
    try:
        assert post(8792, "/judge", {"slot": "J#1", "verdict": "maybe"}) == 400
    finally:
        srv.shutdown()


def test_an_unknown_slot_is_refused(tmp_path):
    """An endpoint is not judgeable, and a typo must not create a phantom slot."""
    srv, _ = serve(tmp_path, 8793)
    try:
        assert post(8793, "/judge", {"slot": "J#0", "verdict": "fits"}) == 400
        assert post(8793, "/judge", {"slot": "NOPE#1", "verdict": "fits"}) == 400
    finally:
        srv.shutdown()


def test_judgements_survive_a_server_restart(tmp_path):
    """The GBL- run split across two sittings; losing saved rows on restart would
    have cost one."""
    srv, f = serve(tmp_path, 8794)
    try:
        assert post(8794, "/judge", {"slot": "J#1", "verdict": "doesnt_fit",
                                     "looked_up": True, "note": "why"}) == 200
    finally:
        srv.shutdown()

    srv2, _ = serve(tmp_path, 8795)
    try:
        _, body = get(8795, "/status")
        assert set(json.loads(body)["missing"]) == {"J#2", "J:note"}
        saved = json.loads(f.read_text("utf-8"))["slots"]["J#1"]
        assert saved == {"verdict": "doesnt_fit", "looked_up": True, "note": "why"}
    finally:
        srv2.shutdown()


def test_complete_only_when_every_slot_and_every_note_is_in(tmp_path):
    srv, _ = serve(tmp_path, 8796)
    try:
        post(8796, "/judge", {"slot": "J#1", "verdict": "fits"})
        post(8796, "/judge", {"slot": "J#2", "verdict": "fits"})
        assert json.loads(get(8796, "/status")[1])["complete"] is False
        post(8796, "/journey_note", {"journey": "J", "note": ""})
        assert json.loads(get(8796, "/status")[1])["complete"] is True
    finally:
        srv.shutdown()


def test_served_page_carries_the_data_and_no_placeholder(tmp_path):
    srv, _ = serve(tmp_path, 8797)
    try:
        _, html = get(8797, "/")
        assert "/*DATA*/" not in html and "/*SAVED*/" not in html
        assert '"role": "interior"' in html or '"role":"interior"' in html
    finally:
        srv.shutdown()
