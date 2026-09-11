# Doc token-turns: a Read's tokens are re-sent on every later turn until compaction.
import json, glob, os, collections, time
BS=chr(92)
roots=[os.path.expanduser('~/.claude/projects/C--dev-music-app'), os.path.expanduser('~/.claude/projects/C--Users-charl-OneDrive-Claude-Projects-music-app')]
def cls(p):
  for k,v in [('docs/README.md','map'),('superpowers/NEXT.md','NEXT'),('TEST-QUEUE','TEST-QUEUE'),('HANDOFF','handoff'),('execution-log','exec-log'),('CLAUDE.md','CLAUDE.md'),('SKILL.md','skill')]:
    if k in p: return v
  return 'other-md' if p.endswith('.md') else 'non-md'
agg=collections.Counter(); tot_cr=0; next_by_date=[]
for r in roots:
  for f in glob.glob(r+'/*.jsonl'):
    ev=[]; tool={}; turn=0; cr=0; compactions=[]
    for line in open(f,encoding='utf-8'):
      try:o=json.loads(line)
      except Exception: continue
      if o.get('type')=='system' and 'compact' in json.dumps(o)[:400].lower(): compactions.append(turn)
      m=o.get('message') or {}
      if o.get('type')=='assistant':
        u=m.get('usage') or {}
        if u.get('cache_read_input_tokens',0)+u.get('input_tokens',0): turn+=1; cr+=u.get('cache_read_input_tokens',0)+u.get('cache_creation_input_tokens',0)+u.get('input_tokens',0)
        for x in m.get('content') or []:
          if isinstance(x,dict) and x.get('type')=='tool_use': tool[x['id']]=(x['name'],x.get('input') or {})
      if o.get('type')=='user' and isinstance(m.get('content'),list):
        for x in m['content']:
          if isinstance(x,dict) and x.get('type')=='tool_result':
            n,i=tool.get(x.get('tool_use_id'),(None,{}))
            t=x.get('content'); s=len(t if isinstance(t,str) else json.dumps(t))
            k=cls(i.get('file_path','').replace(BS,'/')) if n=='Read' else ('tool:'+str(n))
            ev.append((turn,k,s))
            if k=='NEXT': next_by_date.append((time.strftime('%m-%d',time.localtime(os.path.getmtime(f))),os.path.basename(f)[:8],s,bool(i.get('limit'))))
    last=turn
    for (t,k,s) in ev:
      nxt=min([c for c in compactions if c>t] or [last])
      agg[k]+=s/4*(nxt-t)
    tot_cr+=cr
print(f"total input tokens (cached+uncached) across main sessions: {tot_cr:,.0f}")
print("token-turns carried, by source (share of total):")
for k,v in agg.most_common(16): print(f"  {k:18s} {v:>14,.0f}  {100*v/tot_cr:5.1f}%")
print("\nNEXT.md reads by session date (chars, partial?):")
for row in sorted(next_by_date): print("  ",*row)
