import gbl_common as gc


def test_paths_and_constants():
    assert gc.HERE.name == "2026-08-04-gentle-arm-blind-listen"
    assert gc.ROOT.joinpath("builder").is_dir()
    assert gc.SEALED_DIR == gc.ROOT / ".superpowers" / "gbl"
    assert gc.DEPTHS == (0, 10, 20)
    assert gc.TOKENS == ("L", "R")
    assert gc.ARMS == ("V0", "G")


def test_use_cre_makes_cre_common_importable():
    gc.use_cre()
    import cre_common
    assert cre_common.RAMPS["P1a"] > 0  # cited, not restated


def test_in_dir_rejects_traversal():
    for bad in ("../x.json", "a/b.json", "", ".", ".."):
        try:
            gc.in_dir(bad)
            assert False, f"accepted {bad!r}"
        except ValueError:
            pass
    assert gc.in_dir("x.json") == gc.HERE / "x.json"


def test_sealed_path_creates_dir_and_rejects_traversal(tmp_path, monkeypatch):
    monkeypatch.setattr(gc, "SEALED_DIR", tmp_path / "gbl")
    p = gc.sealed_path("gbl_sealed.json")
    assert p == tmp_path / "gbl" / "gbl_sealed.json"
    assert p.parent.is_dir()
    try:
        gc.sealed_path("../oops.json")
        assert False
    except ValueError:
        pass
