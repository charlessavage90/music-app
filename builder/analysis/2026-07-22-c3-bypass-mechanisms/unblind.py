import json
S = json.load(open(r"C:\Users\charl\AppData\Local\Temp\claude\C--Users-charl-OneDrive-Claude-Projects-music-app\e36528b7-26df-4a5f-9b8a-4dd6f76d459c\scratchpad\listen_secret.json", encoding="utf-8"))
ARM = {"V0": "V0 (current)", "A": "A additive", "C": "C waypoint"}

# owner's picks (token). pair2/d15 radio blank but note clearly picks Z.
picks = {
 0: {5:"X",10:"Y",15:"Y",20:"Y"},
 1: {5:"Y",10:"Y",15:"Z",20:"Z"},
 2: {5:"tie",10:"Z",15:"Z",20:"Z"},
}

win = {"V0":0,"A":0,"C":0}
# metric agreement counters: does picked arm optimise each metric among the row's options?
agree = {m:0 for m in ["hubfrac","payload","adamic_adar","overlap_coeff","mean_cn","ceiling_hops"]}
rows = 0
BETTER = {"hubfrac":min,"payload":max,"adamic_adar":max,"overlap_coeff":max,"mean_cn":max,"ceiling_hops":min}

for pi, pair in enumerate(S["pairs"]):
    inv = {tok:arm for arm,tok in pair["mapping"].items()}
    print(f"\n=== pair{pi}: {pair['from']} -> {pair['to']} ({pair['label']}) ===")
    print(f"    token map: " + ", ".join(f"{t}={ARM[a]}" for a,t in pair['mapping'].items()))
    for depth in [5,10,15,20]:
        arms = pair["depths"].get(str(depth)) or pair["depths"].get(depth)
        if not arms: continue
        pick = picks[pi].get(depth)
        picked_arm = inv.get(pick) if pick and pick!="tie" else pick
        # metrics per arm present
        met = {inv[t]: arms[t]["_hidden_metrics"] for t in arms}
        cells = " | ".join(f"{ARM[a]}: hub={m['hubfrac']} pay={m['payload']} AA={m['adamic_adar']} CN={m['mean_cn']} ceil={m['ceiling_hops']}" for a,m in met.items())
        star = ARM.get(picked_arm, picked_arm)
        print(f"  d{depth:>2} PICK={star}")
        print(f"       {cells}")
        if picked_arm in ("V0","A","C"):
            win[picked_arm]+=1; rows+=1
            for mname,better in BETTER.items():
                vals = {a:met[a][mname] for a in met}
                best = better(vals.values())
                if abs(met[picked_arm][mname]-best) < 1e-9:
                    agree[mname]+=1

print("\n\n===== TALLY (clear picks only) =====")
print("arm wins:", {ARM[k]:v for k,v in win.items()})
print(f"\nmetric agreement with the ear ({rows} decisive rows):")
for m,c in sorted(agree.items(), key=lambda x:-x[1]):
    print(f"  {m:<14} {c}/{rows}  ({100*c//rows if rows else 0}%)  -- how often the picked arm optimised this metric")
