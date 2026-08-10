from artistpath_api.config import ApiConfig


def test_validated_weights_are_the_default():
    # The starting weights from findings 6g. Changing these silently would
    # regress path quality, so pin them.
    cfg = ApiConfig()
    assert (cfg.w_sim, cfg.w_jump, cfg.w_floor, cfg.w_hop) == (3.0, 1.0, 1.0, 0.02)


def test_known_relaxes_floor_more_than_dislike():
    # "Know them already" means the popular route is exhausted; it should
    # dig deeper than "not for me" (spec 4.3).
    cfg = ApiConfig()
    assert cfg.floor_relax_known > cfg.floor_relax_dislike > 0


def test_default_graph_path_points_at_the_adopted_artifact():
    # Pins the NAME, not just the extension. Task 11 of the MSW- plan expected
    # to "update the expected name" here and there was no name to update —
    # this asserted only `.endswith(".bin")`, which passes for every artifact
    # ever built and so could not have caught a stale default. Closeout checks
    # this default is not stale; that check now has something to fail on.
    #
    # Adopted 2026-08-10 (CXA-), replacing graph-msw-tu50.bin — which had
    # replaced graph-t15-tiebreakfix.bin on 2026-08-06 (MSW-).
    cfg = ApiConfig()
    assert cfg.graph_path.endswith("graph-cxa-adopted.bin")
