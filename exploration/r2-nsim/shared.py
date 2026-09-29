"""EXPLORATORY. Shared-neighbour overlap (Jaccard) for every edge, cached to cache/jac.npy."""
import time
from pathlib import Path
import numpy as np
from scipy.sparse import csr_matrix

CACHE = Path(__file__).resolve().parent / "cache" / "jac.npy"


def edge_jaccard(off, nbr, n):
    if CACHE.exists():
        j = np.load(CACHE)
        if len(j) == len(nbr):
            return j
    t0 = time.time()
    A = csr_matrix((np.ones(len(nbr), dtype=np.float32), nbr, off), shape=(n, n))
    deg = np.diff(off)
    out = np.zeros(len(nbr), dtype=np.float32)
    B = 4000
    for a in range(0, n, B):
        b = min(n, a + B)
        C = (A[a:b] @ A).multiply(A[a:b]).tocsr()  # common-neighbour counts on existing edges only
        C.sort_indices()
        # align to CSR order of A rows a..b (neighbour lists are sorted by id)
        for u in range(a, b):
            lo, hi = off[u], off[u + 1]
            cs, ce = C.indptr[u - a], C.indptr[u - a + 1]
            cols, vals = C.indices[cs:ce], C.data[cs:ce]
            if len(cols):
                pos = lo + np.searchsorted(nbr[lo:hi], cols)
                out[pos] = vals
    src = np.repeat(np.arange(n), deg)
    inter = out
    out = inter / np.maximum(1, deg[src] + deg[nbr] - inter)
    CACHE.parent.mkdir(exist_ok=True)
    np.save(CACHE, out.astype(np.float32))
    print(f"jaccard computed in {time.time()-t0:.0f}s")
    return out
