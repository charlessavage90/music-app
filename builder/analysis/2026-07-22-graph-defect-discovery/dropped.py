"""Duplicate-aware check + what capfix DROPPED relative to control."""
import sys, numpy as np
sys.path.insert(0, r"C:\Users\charl\OneDrive\Claude Projects\music-app\api\src")
from artistpath_api.graph_store import GraphStore

B = r"C:\Users\charl\OneDrive\Claude Projects\music-app\builder\scratch"
cap = GraphStore.load(B + r"\graph-t15-capfix.bin")
ctl = GraphStore.load(B + r"\graph-t15-control.bin")
dcap, dctl = np.diff(cap.offsets), np.diff(ctl.offsets)

def all_matches(store, deg, nm):
    return [(j, int(deg[j]), float(store.popularity[j]))
            for j in range(len(store.names)) if store.names[j].lower() == nm.lower()]

print("=== duplicate-aware: every entry with these names ===")
for nm in ["Radiohead", "The Beatles", "Coldplay", "Nirvana", "Queen"]:
    c = all_matches(cap, dcap, nm); k = all_matches(ctl, dctl, nm)
    print(f"\n{nm}:")
    print(f"   control: " + (", ".join(f"deg={d} pop={p:.2f}" for _,d,p in k) or "ABSENT"))
    print(f"   capfix : " + (", ".join(f"deg={d} pop={p:.2f}" for _,d,p in c) or "ABSENT"))

# --- what did capfix drop? compare by MBID ---
cap_m = set(cap.mbids); ctl_m = set(ctl.mbids)
dropped = ctl_m - cap_m
print(f"\n\n=== capfix vs control: {len(ctl_m):,} -> {len(cap_m):,}  (dropped {len(dropped):,}) ===")

ctl_idx = {m: i for i, m in enumerate(ctl.mbids)}
drop_pop = np.array([float(ctl.popularity[ctl_idx[m]]) for m in dropped])
all_pop = np.asarray(ctl.popularity, dtype=float)
print(f"dropped popularity: median={np.median(drop_pop):.3f}  mean={drop_pop.mean():.3f}  max={drop_pop.max():.3f}")
print(f"all-graph popularity: median={np.median(all_pop):.3f}  mean={all_pop.mean():.3f}")

# Are the drops disproportionately FAMOUS?
pop_thr = np.sort(all_pop)[int(len(all_pop)*0.99)]   # top-1% popularity
top_pop_mbids = {ctl.mbids[i] for i in np.where(all_pop >= pop_thr)[0]}
lost_famous = top_pop_mbids & dropped
print(f"\ntop-1% most POPULAR artists in control: {len(top_pop_mbids)}")
print(f"   of those, DROPPED by capfix: {len(lost_famous)} ({100*len(lost_famous)/max(len(top_pop_mbids),1):.1f}%)")

print("\n=== 25 most popular artists capfix DROPPED ===")
ranked = sorted(dropped, key=lambda m: -float(ctl.popularity[ctl_idx[m]]))[:25]
for m in ranked:
    i = ctl_idx[m]
    print(f"   {ctl.names[i]:<34} pop={float(ctl.popularity[i]):.3f}  control-deg={int(dctl[i])}")

# survivors: what happened to the most popular artists that DID survive?
print("\n=== 15 most popular SURVIVORS: degree in control -> capfix ===")
cap_idx = {m: i for i, m in enumerate(cap.mbids)}
surv = sorted(ctl_m & cap_m, key=lambda m: -float(ctl.popularity[ctl_idx[m]]))[:15]
for m in surv:
    i, j = ctl_idx[m], cap_idx[m]
    print(f"   {ctl.names[i]:<34} pop={float(ctl.popularity[i]):.2f}  deg {int(dctl[i]):>6} -> {int(dcap[j])}")
