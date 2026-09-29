"""The practice room's columns. Edit this list to add, drop or reorder a variant (see README.md)."""
import os

# (id, label shown on the column, variant file relative to exploration/, one-line description)
VARIANTS = [
    ("today", "Today's app", "baseline/today.py",
     "The shipped router. Each press rebuilds the journey without the artist you pressed."),
    ("tiers", "Fame ladder", "r2-tiers/tiers_keep.py",
     "Each press lowers a fame ceiling one step, set from your two artists; the rest of the journey is held where it still fits."),
    ("overlap", "Shared neighbours", "r2-nsim/dig_overlap_gentle.py",
     "Each press eases toward less famous artists, judging each step by how many neighbours two artists share."),
    ("repair", "Local repair", "r2-repair/finalist_repair.py",
     "Each press keeps the journey and re-routes only the few cards around the one you pressed, through less famous artists."),
    ("simple", "Fame toll", "r2-simple/final_gentle.py",
     "Today's router plus a toll on famous artists that grows with each press, and no weak steps."),
]
if os.environ.get("PR_ALL"):  # runners-up, for curiosity
    VARIANTS += [
        ("tiers_fast", "Fame ladder (faster)", "r2-tiers/tiers_fast.py", "Deeper, keeps less of the previous journey."),
        ("overlap_a", "Shared neighbours (deeper)", "r2-nsim/dig_overlap.py", "Digs deepest; mid-fame pairs go very obscure."),
        ("shaped", "Shaped toll", "r2-shaped/f1_shaped_charge.py", "Toll that is loose next to your two artists and strict in the middle."),
        ("bold", "Fame toll (bold)", "r2-simple/final_bold.py", "Stronger toll."),
    ]
