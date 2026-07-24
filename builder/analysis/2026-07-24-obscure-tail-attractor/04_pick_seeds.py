"""Find real high-pop_raw seeds spanning mutually-distant genres, print their
community + pop_raw so seed choice is auditable (genre inferred from name only)."""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np

API_SRC = Path(__file__).resolve().parents[3] / "api" / "src"
sys.path.insert(0, str(API_SRC))
from artistpath_api.graph_store import GraphStore  # noqa: E402

GRAPH = Path(__file__).resolve().parents[3] / "builder" / "scratch" / "graph-t15-tiebreakfix.bin"
OUT = Path(__file__).resolve().parent
store = GraphStore.load(GRAPH)
pop = store.pop_raw.astype(np.float64)
degrees = np.diff(store.offsets.astype(np.int64))
membership = np.load(OUT / "membership.npy")
name_to_id = {}
for i, nm in enumerate(store.names):
    name_to_id.setdefault(nm, i)

CANDIDATES = [
    ("metal", "Slayer"), ("metal", "Metallica"), ("metal", "Opeth"),
    ("bebop/jazz", "Charlie Parker"), ("bebop/jazz", "Miles Davis"),
    ("bebop/jazz", "John Coltrane"), ("jazz-vocal", "Louis Armstrong"),
    ("classical", "Ludwig van Beethoven"), ("classical", "Johann Sebastian Bach"),
    ("classical", "Wolfgang Amadeus Mozart"), ("classical", "Frédéric Chopin"),
    ("country", "Johnny Cash"), ("country", "Dolly Parton"),
    ("country", "George Strait"), ("country", "Hank Williams"),
    ("hiphop/pop", "Eminem"), ("hiphop/pop", "Drake"),
    ("reggae", "Bob Marley & The Wailers"),
    ("soul/motown", "Marvin Gaye"),
    ("trance", "Tiësto"), ("anime/jpop", "LiSA"),
    ("idm", "Aphex Twin"), ("chillhop", "saib."),
    ("classical", "Erik Satie"), ("classical", "Claude Debussy"),
    ("country", "Willie Nelson"), ("bluegrass", "Bill Monroe"),
]
print(f"{'genre':>14} {'name':>28} {'found':>6} {'comm':>5} {'pop':>6} {'pctl':>6} {'deg':>4}")
for genre, nm in CANDIDATES:
    i = name_to_id.get(nm)
    if i is None:
        print(f"{genre:>14} {nm:>28} {'NO':>6}")
        continue
    pctl = float((pop < pop[i]).mean()*100)
    print(f"{genre:>14} {nm:>28} {'yes':>6} {membership[i]:>5} {pop[i]:>6.3f} {pctl:>6.1f} {int(degrees[i]):>4}")
