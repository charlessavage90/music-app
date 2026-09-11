import asyncio
from dataclasses import dataclass

from lbl_clips import resolve_artist, silent_slots_by_side


@dataclass
class Clip:
    preview_url: str
    title: str
    cover_url: str = ""


@dataclass
class Resolution:
    clip: Clip | None
    count: int


class FakeResolver:
    def __init__(self, tracks, fail=False):
        self.tracks = tracks
        self.fail = fail
        self.calls = []

    async def resolve(self, mbid, name, deezer_artist_id="", index=0):
        self.calls.append((mbid, name, deezer_artist_id, index))
        if self.fail:
            raise RuntimeError("catalogue down")
        if not self.tracks:
            return Resolution(None, 0)
        return Resolution(Clip(self.tracks[index % len(self.tracks)], f"t{index}"), len(self.tracks))


def run(coro):
    return asyncio.run(coro)


def test_up_to_three_distinct_clips_in_the_resolvers_order():
    r = FakeResolver(["u0", "u1", "u2", "u3", "u4"])
    clips = run(resolve_artist(r, "m", "Name", "123", 3))
    assert [c["preview_url"] for c in clips] == ["u0", "u1", "u2"]
    assert {c[2] for c in r.calls} == {"123"} and {c[1] for c in r.calls} == {"Name"}


def test_an_artist_with_one_track_gets_one_clip_and_one_call():
    r = FakeResolver(["only"])
    assert [c["preview_url"] for c in run(resolve_artist(r, "m", "N", "", 3))] == ["only"]
    assert len(r.calls) == 1


def test_duplicates_are_dropped():
    r = FakeResolver(["same", "same"])
    assert len(run(resolve_artist(r, "m", "N", "", 3))) == 1


def test_a_failure_is_a_silent_card_not_a_crash():
    assert run(resolve_artist(FakeResolver(["x"], fail=True), "m", "N", "", 3)) == []
    assert run(resolve_artist(FakeResolver([]), "m", "N", "", 3)) == []


def test_silent_slots_are_counted_per_page_side():
    page = {"pairs": [{"rows": [{"L": {"artists": [{"mbid": "a"}, {"mbid": "b"}]},
                                 "R": {"artists": [{"mbid": "a"}, {"mbid": "c"}]}}]}]}
    assert silent_slots_by_side(page, {"a": [{"preview_url": "x"}], "b": [], "c": [{"preview_url": "y"}]}) == {"L": 1, "R": 0}
