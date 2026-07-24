"""Offline tests for the pure resolver helpers. Run: python test_resolve.py (no network).

These cover the traps that would silently corrupt the count without touching the API:
title->path encoding (the '/' in 'AC/DC'), disambiguation/missing classification, and
window-bounded view summing.
"""

from fetch_pageviews import (
    article_to_rest_path,
    assert_window,
    entity_names,
    is_disambiguation,
    is_musical,
    is_performer,
    name_matches,
    normalise,
    query_is_missing,
    sum_views_in_window,
    WINDOW_START,
    WINDOW_END,
)


def _claim_p31(qid):
    return {"P31": [{"mainsnak": {"datavalue": {"value": {"id": qid}}}}]}


def _claim_p106(qid):
    return {"P106": [{"mainsnak": {"datavalue": {"value": {"id": qid}}}}]}


def test_window_asserts():
    assert_window()  # must not raise


def test_article_encoding_slash():
    # 'AC/DC' is a real title; an unescaped '/' would split the REST path and 404.
    assert article_to_rest_path("AC/DC") == "AC%2FDC", article_to_rest_path("AC/DC")


def test_article_encoding_spaces_to_underscore():
    assert article_to_rest_path("Paul Simon") == "Paul_Simon"
    # Space -> underscore happens BEFORE percent-encoding, so no %20 appears.
    assert "%20" not in article_to_rest_path("Death Cab for Cutie")
    assert article_to_rest_path("Death Cab for Cutie") == "Death_Cab_for_Cutie"


def test_article_encoding_unicode():
    # Non-ASCII titles are percent-encoded, not dropped.
    assert article_to_rest_path("Ólafur Arnalds") == "%C3%93lafur_Arnalds"


def test_disambiguation_true():
    pages = {"123": {"pageid": 123, "title": "Nirvana",
                     "pageprops": {"disambiguation": ""}}}
    assert is_disambiguation(pages) is True


def test_disambiguation_false():
    pages = {"415": {"pageid": 415, "title": "Nirvana (band)",
                     "pageprops": {"wikibase_item": "Q11649"}}}
    assert is_disambiguation(pages) is False


def test_missing_true():
    pages = {"-1": {"ns": 0, "title": "Nonexistent Artist Xyz", "missing": ""}}
    assert query_is_missing(pages) is True


def test_missing_false():
    pages = {"687": {"pageid": 687, "title": "Alice Cooper"}}
    assert query_is_missing(pages) is False


def test_musical_by_genre():
    # P136 (genre) present -> musical, regardless of occupation/type.
    assert is_musical({"P136": [{"mainsnak": {}}]}) is True


def test_musical_by_instrument():
    assert is_musical({"P1303": [{"mainsnak": {}}]}) is True


def test_musical_by_occupation_singer():
    assert is_musical(_claim_p106("Q177220")) is True  # singer


def test_musical_by_band_type():
    assert is_musical(_claim_p31("Q215380")) is True  # musical group


def test_not_musical_place():
    # A town: instance-of human settlement, no music markers -> not musical.
    assert is_musical(_claim_p31("Q3957")) is False


def test_not_musical_empty():
    assert is_musical({}) is False


# --- identity + performer: the clauses that kill the fuzzy false matches ---

def _entity(labels=(), aliases_by_lang=None, p31=()):
    """Build a minimal wbgetentities entity value for testing."""
    return {
        "labels": {f"l{i}": {"value": v} for i, v in enumerate(labels)},
        "aliases": {lang: [{"value": v} for v in vs]
                    for lang, vs in (aliases_by_lang or {}).items()},
        "claims": {"P31": [{"mainsnak": {"datavalue": {"value": {"id": q}}}}] for q in p31}
        if p31 else {},
    }


def test_entity_names_collects_labels_and_aliases():
    e = _entity(labels=["JJ Lin"], aliases_by_lang={"zh": ["林俊傑"], "en": ["JJ"]})
    names = entity_names(e)
    assert "jj lin" in names and "林俊傑" in names and "jj" in names


def test_name_match_cross_language():
    # The load-bearing case: 林俊傑 (query) matches JJ Lin's entity via its zh alias.
    e = _entity(labels=["JJ Lin"], aliases_by_lang={"zh": ["林俊傑"]})
    assert name_matches("林俊傑", e) is True


def test_name_match_rejects_fuzzy_false_positive():
    # CROOVE must NOT match Russell Crowe's entity -- no such label/alias.
    e = _entity(labels=["Russell Crowe"], aliases_by_lang={"en": ["Rusty"]})
    assert name_matches("CROOVE", e) is False


def test_name_match_band_disambig_title():
    # enwiki title is 'Portishead (band)' but the Wikidata label is 'Portishead'.
    e = _entity(labels=["Portishead"])
    assert name_matches("Portishead", e) is True


def test_performer_human():
    assert is_performer({"P31": [{"mainsnak": {"datavalue": {"value": {"id": "Q5"}}}}]}) is True


def test_performer_band():
    assert is_performer(_claim_p31("Q215380")) is True  # musical group


def test_performer_rejects_album():
    # 'Idealism (album)' is instance-of album (Q482994), not a performer.
    assert is_performer(_claim_p31("Q482994")) is False


def test_performer_accepts_band_subtype():
    # The Wishbone Ash lesson: 'rock band' (Q5741069) is a musical-group subclass NOT in
    # any whitelist, but it is not a WORK, so the exclusion rule accepts it.
    assert is_performer(_claim_p31("Q5741069")) is True


def test_performer_rejects_song():
    assert is_performer(_claim_p31("Q7366")) is False  # song


def test_normalise_dotted_and_case():
    assert normalise("saib.") == "saib."
    assert normalise("  Sleepy   Fish ") == "sleepy fish"


def test_sum_views_in_window():
    items = [
        {"timestamp": "2025070100", "views": 100},  # in window
        {"timestamp": "2026060100", "views": 200},  # in window (last month)
        {"timestamp": "2026070100", "views": 999},  # AFTER window -> excluded
        {"timestamp": "2025060100", "views": 500},  # BEFORE window -> excluded
    ]
    total, months = sum_views_in_window(items)
    assert total == 300, total
    assert months == 2, months


def test_sum_views_empty():
    assert sum_views_in_window([]) == (0, 0)


def main():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
    print(f"all {len(tests)} resolver checks passed "
          f"(window {WINDOW_START}..{WINDOW_END})")


if __name__ == "__main__":
    main()
