"""Tests for the TAS tag frame: vocabulary assembly and row parsing.

The vocabulary is pinned by spec section 1 (union genre = LB
genre-whitelisted tags UNION Wikidata P136, through the frozen
ct_common.norm_genre). These tests are what stop it drifting to the widest
tag union, which COH-6 measured as near-identical in the tail and which would
add a second vocabulary for no gain.
"""

from __future__ import annotations

from tas_tags import merge_union_genre
from tas_wikidata import parse_label_rows


def test_union_of_lb_and_wikidata_normalised():
    lb = {"genres": ["Hip-Hop"], "tags": ["hip-hop", "east coast"]}
    assert merge_union_genre(lb, ["Rock music"]) == {"hip hop", "rock"}


def test_missing_sources_give_empty_set_not_error():
    assert merge_union_genre(None, []) == set()
    assert merge_union_genre(None, ["Jazz"]) == {"jazz"}
    assert merge_union_genre({"genres": ["Jazz"], "tags": []}, []) == {"jazz"}


def test_widest_vocabulary_is_not_used():
    # COH-6: the widest union adds ~nothing in the tail. A non-genre tag must
    # not leak in through the LB side.
    assert merge_union_genre({"genres": [], "tags": ["seen live"]}, []) == set()


def test_empty_labels_are_dropped_not_kept_as_empty_string():
    # norm_genre ASCII-folds, so a label with no Latin characters normalises
    # to "". An empty label kept in the set would read as a genre shared by
    # every artist carrying one -- a false agreement between unrelated
    # artists, and it would inflate every Jaccard it touched.
    assert merge_union_genre({"genres": ["パンク"], "tags": []}, []) == set()
    assert merge_union_genre({"genres": [], "tags": []}, ["   "]) == set()


def test_non_latin_only_artists_read_as_UNLABELLED_and_that_is_recorded():
    # A real property of the FROZEN normalisation, not a choice made here:
    # an artist whose only genres are non-Latin has no usable labels and
    # takes the neutral value rather than scoring zero agreement. Correct --
    # overlap across disjoint vocabularies is not computable -- but it means
    # the union genre is a LATIN-SCRIPT vocabulary, and TAS-1's coverage
    # figures must be read as such. COH-2's figures share the property, so
    # the two records stay comparable.
    assert merge_union_genre({"genres": ["パンク", "한국"], "tags": []}, []) == set()
    # Diacritics survive by folding, so this is a script limit, not a
    # language limit: Latin-script non-English labels are kept.
    assert merge_union_genre({"genres": ["Música popular brasileira"], "tags": []}, []) == {
        "musica popular brasileira"
    }


def test_parse_label_rows_groups_multiple_genres_per_artist():
    payload = {
        "results": {
            "bindings": [
                {"mbid": {"value": "m1"}, "genreLabel": {"value": "Rock music"}},
                {"mbid": {"value": "m1"}, "genreLabel": {"value": "Pop"}},
                {"mbid": {"value": "m2"}, "genreLabel": {"value": "Jazz"}},
            ]
        }
    }
    got = parse_label_rows(payload)
    assert got["m1"]["genres"] == ["Pop", "Rock music"]  # sorted, deterministic
    assert got["m2"]["genres"] == ["Jazz"]


def test_parse_label_rows_is_empty_for_no_results():
    assert parse_label_rows({"results": {"bindings": []}}) == {}


def test_parse_label_rows_deduplicates():
    payload = {
        "results": {
            "bindings": [
                {"mbid": {"value": "m1"}, "genreLabel": {"value": "Rock"}},
                {"mbid": {"value": "m1"}, "genreLabel": {"value": "Rock"}},
            ]
        }
    }
    assert parse_label_rows(payload)["m1"]["genres"] == ["Rock"]
