import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "eval"))

from export_paths import neighbour_rank, render_html  # noqa: E402

from tests.conftest import make_store


def test_neighbour_rank_is_one_based_by_descending_score():
    # Node 0's neighbours: 1 (0.9), 2 (0.5), 3 (0.1).
    store = make_store(
        names=list("ABCD"), pop_raw=[0.5] * 4,
        undirected_edges=[(0, 1, 0.9), (0, 2, 0.5), (0, 3, 0.1)],
    )
    assert neighbour_rank(store, 0, 1) == 1
    assert neighbour_rank(store, 0, 2) == 2
    assert neighbour_rank(store, 0, 3) == 3


def test_neighbour_rank_is_none_for_a_non_neighbour():
    store = make_store(
        names=list("ABC"), pop_raw=[0.5] * 3, undirected_edges=[(0, 1, 0.9)]
    )
    assert neighbour_rank(store, 0, 2) is None


def test_render_html_is_self_contained():
    html = render_html(
        artifacts=[{"label": "control", "diagnostics": {"artists": 3, "edges": 4}}],
        panel_name="test",
        rows=[],
    )
    assert "<style" in html
    # A strict CSP applies to nothing here, but an external asset would make
    # the file useless when opened from disk.
    assert "http://" not in html and "https://" not in html


def test_render_html_escapes_hostile_artist_names():
    # Artist names are arbitrary third-party MusicBrainz data — nothing stops
    # one from containing markup. Prove render_html neutralises it rather than
    # just checking the escaped form shows up somewhere in the output.
    hostile = "<script>alert(\"x\")&'</script>"
    rows = [
        {
            "pair": f"{hostile} -> C",
            "cells": [
                {
                    "label": hostile,
                    "hops": [
                        {"name": hostile, "rank": None, "score": None, "degree": 2},
                        {"name": "C", "rank": 1, "score": 0.4, "degree": 2},
                    ],
                    "flagged": True,
                    "reasons": [f"non-musical interior entity: '{hostile}'"],
                }
            ],
        }
    ]
    out = render_html(
        artifacts=[{"label": hostile, "diagnostics": {hostile: hostile}}],
        panel_name=hostile,
        rows=rows,
    )
    # The raw hostile string must never appear unescaped anywhere in the page —
    # not as a live <script> tag, not in an attribute, not in a text node.
    assert "<script>alert(\"x\")&'</script>" not in out
    assert "<script>" not in out
    # Every dangerous character must have been converted to its entity form.
    assert "&lt;script&gt;" in out
    assert "&amp;" in out
    assert "&#x27;" in out
    assert "&quot;" in out


def test_render_html_marks_ceiling_hops():
    rows = [
        {
            "pair": "A -> C",
            "cells": [
                {
                    "label": "control",
                    "hops": [
                        {"name": "A", "rank": None, "score": None, "degree": 2},
                        {"name": "B", "rank": 1, "score": 1.0, "degree": 900},
                        {"name": "C", "rank": 3, "score": 0.4, "degree": 2},
                    ],
                }
            ],
        }
    ]
    html = render_html(artifacts=[{"label": "control", "diagnostics": {}}],
                       panel_name="test", rows=rows)
    assert "ceiling" in html      # the 1.0 hop is marked
