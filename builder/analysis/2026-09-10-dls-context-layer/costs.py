import json, glob, os, collections, time
BS=chr(92)
roots=[os.path.expanduser('~/.claude/projects/C--dev-music-app'), os.path.expanduser('~/.claude/projects/C--Users-charl-OneDrive-Claude-Projects-music-app')]
other=collections.Counter(); othern=collections.Counter(); rows=[]; agent_sizes=collections.defaultdict(list)
for r in roots:
  for f in glob.glob(r+'/*.jsonl')+glob.glob(r+'/*/subagents/*.jsonl'):
    tool={}; first=None; firstuser=None; turns=0; cr=0; cc=0; inp=0; out=0
    atype=None; meta=f[:-6]+'.meta.json'
    if os.path.exists(meta):
      try: atype=json.load(open(meta)).get('agentType')
      except Exception: pass
    for line in open(f,encoding='utf-8'):
      try: o=json.loads(line)
      except Exception: continue
      m=o.get('message') or {}
      if o.get('type')=='user' and firstuser is None and isinstance(m.get('content'),str): firstuser=len(m['content'])
      if o.get('type')=='assistant':
        u=m.get('usage') or {}
        c=u.get('input_tokens',0)+u.get('cache_read_input_tokens',0)+u.get('cache_creation_input_tokens',0)
        if c:
          turns+=1; cr+=u.get('cache_read_input_tokens',0); cc+=u.get('cache_creation_input_tokens',0); inp+=u.get('input_tokens',0); out+=u.get('output_tokens',0)
          if first is None: first=c
        for x in m.get('content') or []:
          if isinstance(x,dict) and x.get('type')=='tool_use': tool[x['id']]=(x['name'],x.get('input') or {})
      if o.get('type')=='user' and isinstance(m.get('content'),list):
        for x in m['content']:
          if isinstance(x,dict) and x.get('type')=='tool_result':
            n,i=tool.get(x.get('tool_use_id'),(None,{}))
            if n=='Read':
              p=i.get('file_path','').replace(BS,'/')
              if p.endswith('.md'):
                t=x.get('content'); s=len(t if isinstance(t,str) else json.dumps(t))
                k=p.split('music-app/')[-1]; other[k]+=s; othern[k]+=1
    rows.append((os.path.getmtime(f),os.path.basename(f)[:8],'sub' if 'subagents' in f else 'main',atype,first,firstuser,turns,cr,cc,inp,out))
    if 'subagents' in f: agent_sizes[atype].append((turns,cr+cc+inp,first or 0))
print("top .md reads by chars:")
for k,v in other.most_common(20): print(f"  {v:>9,} {othern[k]:3d}x {k}")
print("\nsubagents by type: n, median turns, median summed input tokens, median first ctx")
for t,l in agent_sizes.items():
  l.sort(key=lambda z:z[1]); mid=l[len(l)//2]; print(" ",t,len(l),mid[0],f"{mid[1]:,}",f"{sorted(z[2] for z in l)[len(l)//2]:,}")
print("\nrecent main sessions: date id first_ctx first_user_chars turns sum_cache_read sum_cache_create sum_uncached_in out")
for r in sorted([x for x in rows if x[2]=='main'],reverse=True)[:14]:
  print(" ",time.strftime('%m-%d',time.localtime(r[0])),r[1],*r[4:])
