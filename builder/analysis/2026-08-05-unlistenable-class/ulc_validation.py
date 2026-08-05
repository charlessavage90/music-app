"""ULC-V1 / ULC-V2: recover the validation sets from the committed CAU- record.

DIAGNOSTIC ONLY. Adopts nothing, fixes no criterion, sets no bar. It recovers
the artists behind CAU-'s bad-or-unjudgeable verdicts so ULC-G1 has something to
test ULC-D2 against.

WHY THIS EXISTS AS ITS OWN STEP
  findings/2026-08-05-coherence-audit-results.md section 6 reports "22 of 23
  never evaluated by either rule". That denominator includes the audit's own 12
  PLANTED CONTROLS, which were injected by the harness rather than delivered by
  routing -- so filter coverage over them is not a meaningful question and all
  12 are trivially "never evaluated". The real figure is 10 of 11. Recorded as
  ULC-AM0 in the pre-registration; correction owed to that note.

  cau_score.py excludes controls correctly for every CAU- criterion. The defect
  is confined to that one hand-written check.

THE TWO SETS (pre-registration section 1.5)
  ULC-V1  the 7 distinct artists behind a CAN'T TELL verdict -- the TARGET
          class. The findings note reports 8 of the 9 can't-tells record the
          "nothing to listen to" cause.
  ULC-V2  all 11 real artists behind any bad-or-unjudgeable verdict. REPORTED,
          never a trigger (section 2.3): it mixes the target class with ordinary
          stylistic misfits, and a predicate that captured those would be worse,
          not better.

Control identities are read but never written out.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-08-05-unlistenable-class/ulc_validation.py
"""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent.parent.parent
CAU = ROOT / "builder" / "analysis" / "2026-08-04-coherence-audit"
SEALED = ROOT / ".superpowers" / "cau" / "cau_sealed.json"

BAD = ("doesnt_fit", "cant_tell")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    judged = load(CAU / "cau_judgements.json")["slots"]
    page = load(CAU / "cau_page_data.json")["journeys"]
    sealed = load(SEALED)["injections"]

    control_slots = {v["slot"] for v in sealed.values()}

    # Slot ids are journey-id # position-in-artists, and only interior cards
    # become slots -- cau_common.slot_id and cau_score.evaluate agree on this.
    artist_at = {
        f"{j['id']}#{i}": a
        for j in page
        for i, a in enumerate(j["artists"])
        if a["role"] == "interior"
    }

    bad = [s for s, v in judged.items() if v["verdict"] in BAD]
    real = [s for s in bad if s not in control_slots]
    planted = [s for s in bad if s in control_slots]

    def artists(slots: list[str]) -> dict[str, dict]:
        out: dict[str, dict] = {}
        for s in sorted(slots):
            a = artist_at[s]
            out.setdefault(a["mbid"], {
                "name": a["name"],
                "disambiguation": a["disambiguation"],
                "verdicts": [],
            })["verdicts"].append(judged[s]["verdict"])
        return out

    v2 = artists(real)
    v1 = artists([s for s in real if judged[s]["verdict"] == "cant_tell"])

    payload = {
        "status": "diagnostic only -- adopts nothing, fixes no criterion, sets no bar",
        "source": {
            "judgements": "cau_judgements.json",
            "page_data": "cau_page_data.json",
            "controls": "sealed injection file (read, never written out)",
        },
        "ULC_AM0_recount": {
            "bad_slots_total": len(bad),
            "bad_slots_planted": len(planted),
            "bad_slots_real": len(real),
            "distinct_artists_as_section_6_counted": len(
                {artist_at[s]["mbid"] for s in bad}
            ),
            "distinct_artists_planted": len({artist_at[s]["mbid"] for s in planted}),
            "distinct_artists_real": len(v2),
            "note": (
                "section 6's '22 of 23' includes the planted controls in the "
                "denominator; the real figure is 10 of 11 never evaluated"
            ),
        },
        "ULC_V1": v1,
        "ULC_V2": v2,
    }
    out = HERE / "ulc_validation.json"
    out.write_text(json.dumps(payload, indent=1, ensure_ascii=False), encoding="utf-8")

    print(f"ULC-V1 (target class, can't-tell): {len(v1)} artists", flush=True)
    for mbid, a in v1.items():
        print(f"  {mbid}  {a['name']}", flush=True)
    print(f"\nULC-V2 (all real bad verdicts):    {len(v2)} artists", flush=True)
    print(f"\nplanted controls among bad slots:  {len(planted)} "
          f"(excluded from both sets)", flush=True)
    print(f"wrote {out.name}", flush=True)


if __name__ == "__main__":
    main()
