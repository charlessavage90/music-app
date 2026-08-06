"""All API tunables. No magic numbers elsewhere in the package."""

from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class ApiConfig:
    # --- graph ----------------------------------------------------------
    # Default is the ADOPTED artifact, by name — flipped at each adoption
    # (spec 2026-07-23 §1 decision 4; closeout checks this default is not
    # stale). Adopted 2026-08-06 by MSW-: the trimmed-union build carrying
    # fame_lb, replacing graph-t15-tiebreakfix.bin. Its identity (sha256, node
    # and edge counts) is owned by the MSW- execution log's Task 9 section and
    # by the artifact's own manifest sidecar — cited, never transcribed here.
    # It is gitignored: a fresh clone copies it (or the archive) from another
    # machine and verifies the sha256 against the sidecar.
    # The retired 5k dev fixture is NOT a substitute — its snowball shape
    # misrepresents the obscure tail, which is what bypass work exercises.
    # One env var swaps the graph without code changes.
    graph_path: str = os.environ.get(
        "ARTISTPATH_GRAPH", "../builder/scratch/graph-msw-tu50.bin"
    )
    # Expected sha256 of the artifact. Empty skips verification (local dev);
    # production sets it and the service refuses to boot on a mismatch. The
    # value is in the artifact's manifest sidecar — do not transcribe it by
    # hand (DEP-24).
    graph_sha256: str = os.environ.get("ARTISTPATH_GRAPH_SHA256", "")
    # Shared secret CloudFront injects on both behaviours. App Runner publishes
    # its own public URL and has no OAC equivalent, so without this the
    # password gate protects the SPA and not the API (TR-7). Empty disables the
    # check: that is local dev and the whole test suite.
    origin_secret: str = os.environ.get("ARTISTPATH_ORIGIN_SECRET", "")

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

    # "Know them already" ramp, priced in FAME percentile (fame_lb_pctl —
    # ListenBrainz listener rank within the served artifact's own population),
    # NOT in raw popularity like the two terms above. Each press of "know them
    # already" adds a toll on widely-listened-to artists, so the tenth press
    # pushes much harder toward the obscure than the first does.
    #
    # 0.0 = off, and off means the term is not applied AT ALL rather than
    # applied as `+ 0.0`: with the knob at zero, or with zero presses, the cost
    # arithmetic is the one that shipped before this existed (MSW-G2).
    #
    # ADOPTED 2026-08-06 (MSW-) at 0.01 — the `P1a` arm of the CRE- sweep,
    # which is the configuration the GBL- blind listen heard and the CAU-
    # audit judged. The value's source is cre_common.py's RAMPS; flipped from
    # 0.0 in one commit with BuilderConfig's cap_strategy and require_fame.
    #
    # ⚠ This adoption OVERRIDES the GBL- null on the owner's authority (margin
    # 3 against a bar of 5; the pre-registered consequence was "production
    # stands"). Neither GBL- nor CAU- licensed it — see the MSW- execution
    # log. Never cite this default as evidence-backed adoption.
    #
    # Requires an artifact carrying fame: create_app refuses to boot if this is
    # non-zero over one that does not (and the router degrades to ignoring the
    # term rather than raising mid-request, as a second line).
    w_known_ramp_fame_pctl: float = 0.01

    # --- bypass shaping (spec 4.3) --------------------------------------
    floor_relax_known: float = 0.15    # each "known" bypass softens the floor
    floor_relax_dislike: float = 0.08  # each "dislike" bypass softens it less
    avoid_penalty: float = 0.5         # cost added at a disliked artist's neighbours
    avoid_decay: float = 0.5           # penalty falls off per hop
    avoid_radius: int = 2              # hops the penalty reaches

    # --- search ---------------------------------------------------------
    search_limit: int = 10

    # --- request bounds (G3-S3) -----------------------------------------
    # A body larger than this is refused before it is parsed. The schema bounds
    # in models.py cannot fire until the whole body has been read into memory,
    # which is the cost being avoided: the review measured a 2,000,000-element
    # `sources` array buffering ~70 MB before the handler's two-source check
    # rejected it. 64 KiB is ~30x the largest legitimate request (200
    # exclusions at 64 bytes of id, plus JSON overhead).
    max_body_bytes: int = 64 * 1024

    # --- CORS (stage 3a) ------------------------------------------------
    # Allowed browser origins for the SPA, comma-separated in
    # ARTISTPATH_CORS_ORIGINS. The default is EMPTY — no origin is allowed.
    #
    # It defaulted to http://localhost:5173 until 2026-07-27, and that default
    # was live in PRODUCTION, because the fix TR-8 prescribed does not survive
    # contact with AWS: the stack sets this variable to the empty string, and an
    # empty-valued environment variable does not reach a running App Runner
    # service. Measured — drift detection reported it REMOVE'd, and the deployed
    # API echoed access-control-allow-origin: http://localhost:5173 back to a
    # live probe, with a made-up origin correctly getting nothing.
    #
    # So the guarantee lives HERE now, where absence is safe, rather than in a
    # value something downstream has to carry successfully. Nothing is lost in
    # dev: frontend/vite.config.ts proxies /api to :8000, so the browser only
    # ever talks to the Vite origin and no CORS header is involved either way.
    # A genuinely cross-origin deployment sets the variable explicitly.
    cors_origins: tuple[str, ...] = field(
        default_factory=lambda: tuple(
            o.strip()
            for o in os.environ.get("ARTISTPATH_CORS_ORIGINS", "").split(",")
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
    # Top tracks for a SPECIFIC Deezer artist id, used when MusicBrainz records
    # one. No name matching, so it cannot return a different artist of the same
    # name (`BYP-13`). Proven by builder/analysis/.../tail_clips.py `id_path`.
    deezer_artist_url: str = "https://api.deezer.com/artist"
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
    # collisions. 25 is a judgement, not a measurement: the one documented
    # case (roadmap C1) needed 2, and nobody has measured how deep the worst
    # case goes. Raise it if cards come back silent for artists that
    # obviously have tracks.
    clip_search_limit: int = 25

    # --- clip circuit breaker (G3-A4 / G3-S2) ---------------------------
    # Consecutive unavailable responses from ONE catalogue before we stop
    # calling it. 5 rather than 1 or 2: a single transient error must not
    # silence every card for a minute, which would be worse than the defect.
    clip_breaker_threshold: int = 5
    # How long to leave it alone afterwards. 60 s is a judgement, not a
    # measurement — neither catalogue documents its rate-limit window. The
    # first request after the cooldown is the probe; if it fails the breaker
    # re-opens immediately, so a service that stays down costs one call a
    # minute rather than five.
    clip_breaker_cooldown_s: float = 60.0
