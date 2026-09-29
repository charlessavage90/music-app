"""Builds the two self-contained finalist files from v2.py + lib2.py with settings baked in."""
import re
lib = open('lib2.py', encoding='utf-8').read()
v2 = open('v2.py', encoding='utf-8').read()
lib_body = lib.split('import heapq\n', 1)[1]
body = v2.split('from lib2 import route_h, baseline\n', 1)[1]
pstart = body.index('P = dict(')
pend_marker = 'P.update(json.loads(os.environ.get("R2", "{}")))\n'
pend = body.index(pend_marker) + len(pend_marker)
body = body[:pstart] + '@@PARAMS@@' + body[pend:]
body = re.sub(r'_LOG = os\.environ\.get\("R2LOG"\)\n\n\ndef _log\(msg\):\n(?:(?: {4,}).*\n)+', '', body)
body = re.sub(r' {16}if P\.get\("DBG"\).*\n.*\n', '', body)
body = re.sub(r' {4}_log\(.*\n(?: {8,}.*\n)*', '', body)
body = body.replace('    t0 = time.time()\n', '')
assert '_log' not in body, [l for l in body.splitlines() if '_log' in l]
assert 'os.environ' not in body and 'time.' not in body
base = dict(MARGIN=0.10, T_OFF=0.12, D_OFF=0.35, W_F=1.0, W_D=1.0, W_HOP=0.5,
            LEN_EXTRA=3, LEN_MIN=10, EXTRA_W=2, SWAP_MIN=0.6, W_PULL=3.0, SHORT_MIN=0.6,
            MAXPOPS=8000, W_X=1.0, EDGE_MINSIM=None, REACH=1, BAND_XEDGE=1, REACH_W=[2, 3, 4, 5],
            MINSIM=0.6, MINSIM_PULL=0.4, DIVE_MAX=0.5,
            WINDOWS=[1, 2, 3, 4, 99], FULL=0, PULL1=1,
            DRIFT=0, DRIFT_MARGIN=0.05, DRIFT_DROP=0.25, DRIFT_MINSIM=0.6)
DOC1 = '''"""Pressing Dig deeper keeps your journey and re-routes only the few cards around the artist you pressed, through similar but less famous artists, so the journey gets more obscure where you press without growing much.

EXPLORATORY (r2-repair finalist A, "local repair"). Self-contained: settings baked in, no env vars.
Interface: journey(ctx, s, t, pressed, prev) as in exploration/kit/qlook.py. Press 0 = today's router.
Press k = repair(journey(pressed[:-1]), pressed[-1]) -- the app replays the `known` list in order.
How a press works (x = pressed artist):
  1. "band": re-route a window of 1..4 cards either side of x. Every new card is at least 10 points
     less famous than x (the card next to an endpoint included); the router prefers cards 12+ points
     below x, pays for cards more than 35 points below (and never admits cards 50+ below), prefers
     x's own similar artists, and takes no step weaker than similarity 0.6.
  2. "reach" (x next to an endpoint): a famous endpoint's neighbours are often all famous, so that
     card may stay famous, but the 1..4 cards behind it must each come back 10 points less famous.
  3. "pull0"/"pull1": if nothing less famous fits, take the least famous similar option (famous-for-
     famous next to an exhausted endpoint), in the interior never more famous than x.
  4. last resorts: drop x if its neighbours link directly; else an uncapped windowed swap. Never
     a regeneration from scratch (a reset would undo every earlier press).
  Monotone: across a window the new cards' fames, sorted, may not exceed the old ones anywhere.
  Length budget: max(press-0 length + 3, 10); an over-long detour is paid for by dropping cards whose
  neighbours link directly. Routing: hop-bounded Dijkstra, typically < 0.1 s, worst ~2.5 s per press.
"""'''
DOC2 = DOC1.replace(
    'so the journey gets more obscure where you press without growing much.',
    'then nudges up to two other cards to similar, slightly less famous artists.').replace(
    'finalist A, "local repair"', 'finalist B, "repair plus drift"').replace(
    '  Monotone:', '  5. drift: then up to 2 in-place swaps elsewhere (most famous cards first), each to an artist\n'
    '     5-25 points less famous whose links to both neighbours are >= 0.6 and not weaker than before.\n  Monotone:')
for name, doc, drift in (('finalist_repair.py', DOC1, 0), ('finalist_repair_drift.py', DOC2, 2)):
    p = dict(base)
    p['DRIFT'] = drift
    ptxt = 'P = dict(\n' + ''.join(f'    {k}={v!r},\n' for k, v in p.items()) + ')\n'
    b = body.replace('@@PARAMS@@', ptxt).replace('import json\nimport os\nimport time\n\n', '').lstrip()
    out = doc + '\nimport heapq\n\n\n' + lib_body.strip() + '\n\n\n' + b
    open(name, 'w', encoding='utf-8').write(out)
