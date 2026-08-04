import json
import threading
import urllib.error
import urllib.request

import gbl_page


def _post(port, path, body):
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def _get(port, path):
    with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}") as r:
        return r.status, r.read().decode("utf-8")


def _serve(tmp_path, page_data=None, clips=None):
    page_data = page_data or {"pairs": [{"key": "ma|mb", "a": "A", "b": "B",
                                         "rows": [
        {"depth": d, "L": {"artists": []}, "R": {"artists": []}}
        for d in (0, 10, 20)]}]}
    srv = gbl_page.make_server(page_data, clips or {},
                               verdict_file=tmp_path / "gbl_verdicts.json",
                               port=0)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, srv.server_address[1]


def test_verdicts_and_claims_are_persisted_and_status_completes(tmp_path):
    srv, port = _serve(tmp_path)
    try:
        status, body = _get(port, "/")
        assert status == 200 and "GBL" in body
        # The WGLL-bound instruction: the ear is the instrument, and a lookup
        # mid-listen would contaminate it.
        assert "No Spotify or\nmonthly-listener lookups until every verdict is saved." in body

        assert json.loads(_get(port, "/status")[1])["complete"] is False
        for d in ("0", "10", "20"):
            _post(port, "/verdict", {"pair": "ma|mb", "depth": d, "pick": "L"})
        _post(port, "/claims", {"pair": "ma|mb", "q1": "L", "q2": "none",
                                "q2_collapse": "", "notes": "n"})
        st = json.loads(_get(port, "/status")[1])
        assert st["complete"] is True

        saved = json.loads((tmp_path / "gbl_verdicts.json").read_text("utf-8"))
        assert saved["rows"]["ma|mb"]["10"] == "L"
        assert saved["claims"]["ma|mb"]["notes"] == "n"
    finally:
        srv.shutdown()


def test_verdict_rejects_unknown_pair_and_bad_pick(tmp_path):
    srv, port = _serve(tmp_path)
    try:
        for bad in ({"pair": "zz", "depth": "0", "pick": "L"},
                    {"pair": "ma|mb", "depth": "0", "pick": "V0"},
                    {"pair": "ma|mb", "depth": "5", "pick": "L"}):
            try:
                _post(port, "/verdict", bad)
                assert False, bad
            except urllib.error.HTTPError as e:
                assert e.code == 400
    finally:
        srv.shutdown()


def test_a_split_sitting_resumes_from_the_saved_file(tmp_path):
    # The owner is told sittings can be split; if a restart dropped his saved
    # rows the run-state gate would refuse a read on work he had already done.
    srv, port = _serve(tmp_path)
    try:
        _post(port, "/verdict", {"pair": "ma|mb", "depth": "10", "pick": "R"})
    finally:
        srv.shutdown()

    srv2, port2 = _serve(tmp_path)
    try:
        st = json.loads(_get(port2, "/status")[1])
        assert "ma|mb:d10" not in st["missing"]
        assert "ma|mb:d0" in st["missing"]
    finally:
        srv2.shutdown()


def test_the_page_never_carries_an_arm_label(tmp_path):
    # The page is the last place arm identity could leak, and it is the one the
    # owner actually looks at. Assert against the served HTML, not the data.
    page_data = {"pairs": [{"key": "ma|mb", "a": "The Cramps", "b": "B", "rows": [
        {"depth": d,
         "L": {"artists": [{"mbid": "m1", "name": "Louis Armstrong"}]},
         "R": {"artists": [{"mbid": "m2", "name": "Y"}]}}
        for d in (0, 10, 20)]}]}
    srv, port = _serve(tmp_path, page_data,
                       {"m1": {"preview_url": "u", "title": "t", "cover_url": "c"}})
    try:
        body = _get(port, "/")[1]
        assert "The Cramps" in body          # names survive
        assert "Louis Armstrong" in body
        for token in ("B-S1", "tiebreakfix", "P1a", "adopted", "gentle"):
            assert token not in body, token
    finally:
        srv.shutdown()


def test_the_two_verdict_questions_are_the_frozen_wording(tmp_path):
    # GBL-Q1/Q2 wording is frozen by the spec and owner-reviewed; the page is
    # where it reaches him, so drift is caught here rather than after the run.
    srv, port = _serve(tmp_path)
    try:
        body = _get(port, "/")[1]
        assert ("As the presses accumulate, which side, if either, delivers "
                "more artists new to you?") in body
        assert ("Which side, if either, holds together better as a journey "
                "— each step a sensible next listen?") in body
        assert "collapse into a random walk into obscurity" in body
    finally:
        srv.shutdown()
