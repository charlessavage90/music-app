import json, sys
init=None; result=None
for line in open(sys.argv[1], encoding='utf-8'):
    try: o=json.loads(line)
    except Exception: continue
    if o.get('type')=='system' and o.get('subtype')=='init': init=o
    if o.get('type')=='result': result=o
print("init keys:", sorted(init.keys()) if init else None)
if init:
    for k in ('tools','slash_commands','skills','agents','mcp_servers','plugins'):
        v=init.get(k)
        if v is None: continue
        names=[x if isinstance(x,str) else (x.get('name') or json.dumps(x)) for x in v]
        hit=[n for n in names if any(t in n.lower() for t in ('notion','session-start','consultant'))]
        print(f"  {k}: n={len(names)} matches={hit}")
print("result:", (result or {}).get('result'))
print("denials:", (result or {}).get('permission_denials'))
