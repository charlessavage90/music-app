import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', 'kit')); sys.path.insert(0, HERE)
from qlook import Ctx, load_variant
ctx = Ctx()
mod = load_variant(sys.argv[1])
s, t = ctx.lookup(sys.argv[2]), ctx.lookup(sys.argv[3]); K = int(sys.argv[4])
pressed, prev = [], None
for k in range(K + 1):
    p = mod.journey(ctx, s, t, list(pressed), prev)
    print(k, ' > '.join(f'{ctx.names[v]}({ctx.pl[v]*100:.0f})' for v in p))
    x = min([v for v in p[1:-1] if v not in pressed], key=ctx.key); pressed.append(x); prev = p
    print('   press', ctx.names[x])
