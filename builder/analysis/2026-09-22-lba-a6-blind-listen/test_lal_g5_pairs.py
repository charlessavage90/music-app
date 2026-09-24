"""`lal_g5_pairs.py`: journeys and rerolls are folded correctly and nothing else is read."""
import json

from lal_g5_pairs import journeys, path_events, render


def ev(src, tgt, depth=0, event="path"):
    return json.dumps({"event": event, "source": {"name": src}, "target": {"name": tgt}, "bypass_depth": depth})


def test_only_path_events_are_read_and_junk_lines_are_skipped():
    lines = ['INFO: 127.0.0.1 - "POST /api/path HTTP/1.1" 200 OK', "{not json", ev("A", "B", event="clip"), ev("A", "B")]
    assert [e["source"]["name"] for e in path_events(lines)] == ["A"]


def test_rerolls_count_against_the_journey_before_them_and_a_new_pair_opens_a_new_line():
    events = list(path_events([ev("A", "B"), ev("A", "B", 1), ev("A", "B", 2), ev("C", "D"), ev("A", "B")]))
    assert render(journeys(events)) == ["A → B  (rerolls: 2)", "C → D  (rerolls: 0)", "A → B  (rerolls: 0)"]


def test_a_log_that_starts_mid_walk_still_records_the_pair():
    events = list(path_events([ev("A", "B", 3), ev("A", "B", 4)]))
    assert render(journeys(events)) == ["A → B  (rerolls: 2)"]
