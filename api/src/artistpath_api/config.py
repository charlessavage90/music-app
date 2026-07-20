"""All API tunables. No magic numbers elsewhere in the package."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ApiConfig:
    # --- graph ----------------------------------------------------------
    # Dev default is the committed 5k graph; production sets ARTISTPATH_GRAPH
    # to the 75k artifact. One env var swaps the graph without code changes.
    graph_path: str = os.environ.get(
        "ARTISTPATH_GRAPH", "../builder/scratch/graph-5k.bin"
    )

    # --- cost function weights (findings 6g) ----------------------------
    w_sim: float = 3.0    # reward strong similarity
    w_jump: float = 1.0   # punish popularity cliffs
    w_floor: float = 1.0  # discourage diving into obscurity
    w_hop: float = 0.02   # per-hop cost; low so paths can be long and smooth
    w_avoid: float = 1.0  # "not for me" neighbourhood penalty

    # --- bypass shaping (spec 4.3) --------------------------------------
    floor_relax_known: float = 0.15    # each "known" bypass softens the floor
    floor_relax_dislike: float = 0.08  # each "dislike" bypass softens it less
    avoid_penalty: float = 0.5         # cost added at a disliked artist's neighbours
    avoid_decay: float = 0.5           # penalty falls off per hop
    avoid_radius: int = 2              # hops the penalty reaches

    # --- search ---------------------------------------------------------
    search_limit: int = 10

    # --- clips ----------------------------------------------------------
    deezer_search_url: str = "https://api.deezer.com/search"
    itunes_search_url: str = "https://itunes.apple.com/search"
    # "memory" (local dev, default) or "dynamo" (production). Memory means the
    # server boots and serves paths without any AWS configuration.
    clip_cache: str = os.environ.get("ARTISTPATH_CLIP_CACHE", "memory")
    clip_table_name: str = os.environ.get("ARTISTPATH_CLIP_TABLE", "artistpath-clips")
    clip_ttl_days: int = 30
    clip_http_timeout: float = 10.0
