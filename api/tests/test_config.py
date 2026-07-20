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


def test_default_graph_path_points_at_an_artifact():
    assert ApiConfig().graph_path.endswith(".bin")
