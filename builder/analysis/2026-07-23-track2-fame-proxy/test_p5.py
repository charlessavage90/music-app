"""P5 normalisation tests. Run: python test_p5.py (no framework, no network)."""

from fetch_fame import p5_normalise as N


def check(a, b, why):
    if N(a) != N(b):
        raise AssertionError(f"{why}: {a!r} -> {N(a)!r} != {b!r} -> {N(b)!r}")


def check_ne(a, b, why):
    if N(a) == N(b):
        raise AssertionError(f"{why}: {a!r} and {b!r} both -> {N(a)!r}, should differ")


def main():
    # The record's own hyphen trap: U+2010 must fold to ASCII '-'.
    check("blink‐182", "blink-182", "U+2010 hyphen")
    # NFKC alone does NOT fix this — guard against someone dropping the fold step.
    import unicodedata
    assert unicodedata.normalize("NFKC", "blink‐182") != "blink-182", (
        "if this fails, NFKC now handles U+2010 and the note in the module is stale"
    )
    # Other dashes seen in artist names.
    check("Composer – Work", "Composer - Work", "en dash")
    check("A—B", "A-B", "em dash")
    check("Motörhead", "Motörhead", "diacritic identity (NFC vs NFD)")
    # Curly quotes and apostrophes.
    check("Sinéad O’Connor", "Sinéad O'Connor", "curly apostrophe")
    check("“Heroes”", '"Heroes"', "curly double quotes")
    # Whitespace and case.
    check("The  Byrds", "the byrds", "collapse whitespace + casefold")
    check(" Nirvana ", "Nirvana", "strip")
    check("AC/DC", "ac/dc", "slash preserved, casefold")
    # CJK left intact (must still equal itself, must not be mangled).
    check("林俊傑", "林俊傑", "CJK identity")
    check_ne("林俊傑", "林俊杰", "traditional vs simplified must NOT collapse")
    # A real distinction must survive.
    check_ne("The Byrds", "The Birds", "genuine spelling difference preserved")

    print("all P5 normalisation checks passed")


if __name__ == "__main__":
    main()
