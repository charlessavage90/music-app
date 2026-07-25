"""All API tunables. No magic numbers elsewhere in the package."""

from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class ApiConfig:
    # --- graph ----------------------------------------------------------
    # Default is the ADOPTED 75k artifact, by name — flipped at each adoption
    # (spec 2026-07-23 §1 decision 4; closeout checks this default is not
    # stale). It is gitignored: a fresh clone copies it (or the archive) from
    # another machine and verifies the sha256 against
    # docs/superpowers/findings/2026-07-23-tiebreak-fix-adoption.md.
    # The retired 5k dev fixture is NOT a substitute — its snowball shape
    # misrepresents the obscure tail, which is what bypass work exercises.
    # One env var swaps the graph without code changes.
    graph_path: str = os.environ.get(
        "ARTISTPATH_GRAPH", "../builder/scratch/graph-t15-tiebreakfix.bin"
    )

    # --- cost function weights (findings 6g) ----------------------------
    # THIS BLOCK IS THE ONLY DEFINITION OF THESE DEFAULTS. Prose that needs
    # them cites this dataclass rather than copying the numbers; two copies
    # went stale once already.
    #
    # Currency note: `w_jump` and `w_floor` both price RAW popularity
    # (`GraphStore.pop_raw`), not percentile. Log §2.12 records that the two
    # diverge sharply at the top of the distribution, and repricing them in
    # percentile currency is exactly what the Track 2 sweep tests
    # (specs/2026-07-23-track2-preregistration.md §1.3).
    w_sim: float = 3.0    # reward strong similarity
    w_jump: float = 1.0   # punish raw-popularity cliffs
    w_floor: float = 1.0  # discourage diving below the raw-popularity floor
    w_hop: float = 0.02   # per-hop cost; low so paths can be long and smooth
    w_avoid: float = 1.0  # "not for me" neighbourhood penalty
    # Penalty for routing through high-DEGREE artists. Degree, not fame: log
    # §2.6 records that the top-1%-by-degree set is largely insular micro-genre
    # artists, so this term does not penalise famous artists and never did.
    # Default 0.0 keeps it a no-op; the 2026-07-21 baseline showed
    # hub-traversal is topological. Set from a tuned search.
    w_degree_hub: float = 0.0

    # --- bypass shaping (spec 4.3) --------------------------------------
    floor_relax_known: float = 0.15    # each "known" bypass softens the floor
    floor_relax_dislike: float = 0.08  # each "dislike" bypass softens it less
    avoid_penalty: float = 0.5         # cost added at a disliked artist's neighbours
    avoid_decay: float = 0.5           # penalty falls off per hop
    avoid_radius: int = 2              # hops the penalty reaches

    # --- search ---------------------------------------------------------
    search_limit: int = 10

    # --- CORS (stage 3a) ------------------------------------------------
    # Allowed browser origins for the SPA. Dev default is the Vite server;
    # production sets ARTISTPATH_CORS_ORIGINS (comma-separated) to the
    # deployed frontend origin. Not needed when the SPA is proxied same-origin.
    cors_origins: tuple[str, ...] = field(
        default_factory=lambda: tuple(
            o.strip()
            for o in os.environ.get(
                "ARTISTPATH_CORS_ORIGINS", "http://localhost:5173"
            ).split(",")
            if o.strip()
        )
    )

    # --- clips ----------------------------------------------------------
    deezer_search_url: str = "https://api.deezer.com/search"
    itunes_search_url: str = "https://itunes.apple.com/search"
    # Per-track lookups. A cached track's preview URL is re-resolved through
    # these on every request, because the URL Deezer signs expires in under
    # an hour while the track it points at does not (C2).
    deezer_track_url: str = "https://api.deezer.com/track"
    itunes_lookup_url: str = "https://itunes.apple.com/lookup"
    # "memory" (local dev, default) or "dynamo" (production). Memory means the
    # server boots and serves paths without any AWS configuration.
    clip_cache: str = os.environ.get("ARTISTPATH_CLIP_CACHE", "memory")
    clip_table_name: str = os.environ.get("ARTISTPATH_CLIP_TABLE", "artistpath-clips")
    clip_ttl_days: int = 30
    clip_http_timeout: float = 10.0
    # Both catalogues match song *titles* as well as artist names, so the top
    # hit is routinely someone else's track (C1: searching "The Format"
    # returns a song called The Format by AZ above the band). We ask for a
    # page of results and keep the first whose artist matches the one we
    # asked for, so this has to be wide enough to reach past the title
    # collisions. 25 covers the observed cases with one request.
    clip_search_limit: int = 25
