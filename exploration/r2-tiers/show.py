import json, sys
from pathlib import Path
q = Path(sys.argv[1]).resolve()
if Path(__file__).resolve().parents[1] not in q.parents:
    raise SystemExit('refusing path outside exploration/')
d = json.loads(q.read_text(encoding='utf-8'))
idx = [int(x) for x in sys.argv[2].split(',')] if len(sys.argv) > 2 else range(len(d['rows']))
for i in idx:
    r = d['rows'][i]
    print('##', i, r['source_name'], '->', r['target_name'])
    for l in r['ladder']:
        print(' p%d' % l['k'], ' > '.join(f'{n} ({p*100:.0f})' for n, p in zip(l['names'][1:-1], l['pctl'][1:-1])))
