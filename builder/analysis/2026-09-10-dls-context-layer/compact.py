import json, glob, os
roots=[os.path.expanduser('~/.claude/projects/C--dev-music-app'), os.path.expanduser('~/.claude/projects/C--Users-charl-OneDrive-Claude-Projects-music-app')]
n=0; with_compact=0; total_compacts=0; closeout_after=0; closeout_total=0; ss_after=0
for r in roots:
  for f in glob.glob(r+'/*.jsonl'):
    n+=1; compacts=0; seen_compact=False
    for line in open(f,encoding='utf-8'):
      try:o=json.loads(line)
      except Exception: continue
      if o.get('isCompactSummary') or (o.get('type')=='system' and o.get('subtype')=='compact_boundary'):
        if o.get('type')=='system': compacts+=1
        seen_compact=True
      m=o.get('message') or {}
      if o.get('type')=='assistant':
        for x in m.get('content') or []:
          if isinstance(x,dict) and x.get('type')=='tool_use' and x.get('name')=='Skill':
            s=(x.get('input') or {}).get('skill')
            if s=='closeout':
              closeout_total+=1; closeout_after+=seen_compact
    total_compacts+=compacts; with_compact+=compacts>0
print(f"main sessions={n} sessions_with_compaction={with_compact} total_compactions={total_compacts} closeout_invocations={closeout_total} closeout_after_a_compaction={closeout_after}")
