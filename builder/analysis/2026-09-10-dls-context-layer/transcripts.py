"""Mine session transcripts for what documentation sessions actually read, and at what cost."""
import json, glob, os, re, sys, collections

# Only Claude Code project directories are read: each argument must resolve under
# ~/.claude/projects, so the script cannot be pointed at arbitrary paths.
BASE = os.path.realpath(os.path.expanduser("~/.claude/projects"))
roots = []
for arg in sys.argv[1:]:
    root = os.path.realpath(arg)
    if os.path.commonpath([BASE, root]) != BASE:
        sys.exit(f"refusing {arg!r}: not under {BASE}")
    roots.append(root)
files = []
for r in roots:
    files += glob.glob(os.path.join(r, "*.jsonl"))
    files += glob.glob(os.path.join(r, "*", "subagents", "*.jsonl"))

DOC_KEYS = {
    "docs/README.md": "README(map)",
    "superpowers/NEXT.md": "NEXT",
    "NEXT-ARCHIVE.md": "NEXT-ARCHIVE",
    "CLAUDE.md": "CLAUDE.md",
    "closeout/SKILL.md": "closeout",
    "session-start/SKILL.md": "session-start",
    "TEST-QUEUE.md": "TEST-QUEUE",
    "PRODUCT-REQUIREMENTS.md": "PRD",
    "WHAT-GOOD-LOOKS-LIKE.md": "WGLL",
    "scoring-adjudication.md": "adjudication",
    "HANDOFF": "HANDOFF-*",
    "execution-log": "exec-logs",
    "memory/": "memory",
}

def key_for(path):
    p = path.replace("\\", "/")
    for k, v in DOC_KEYS.items():
        if k in p:
            return v
    if p.endswith(".md"):
        return "other .md"
    return None

agg_reads = collections.Counter()
agg_chars = collections.Counter()
agg_grep = collections.Counter()
errors = collections.Counter()
skills = collections.Counter()
agents = collections.Counter()
per_session = []

for f in sorted(files):
    tool_by_id = {}
    reads = collections.Counter(); chars = collections.Counter()
    first_inputs = None; max_ctx = 0; n_assistant = 0
    readme_partial = 0
    try:
        lines = open(f, encoding="utf-8").read().splitlines()
    except Exception:
        continue
    for line in lines:
        try:
            o = json.loads(line)
        except Exception:
            continue
        msg = o.get("message") or {}
        if o.get("type") == "assistant":
            u = msg.get("usage") or {}
            ctx = (u.get("input_tokens", 0) + u.get("cache_read_input_tokens", 0)
                   + u.get("cache_creation_input_tokens", 0))
            if ctx:
                n_assistant += 1
                if first_inputs is None:
                    first_inputs = ctx
                max_ctx = max(max_ctx, ctx)
            for c in msg.get("content") or []:
                if isinstance(c, dict) and c.get("type") == "tool_use":
                    name = c.get("name"); inp = c.get("input") or {}
                    tool_by_id[c.get("id")] = (name, inp)
                    if name == "Read":
                        k = key_for(inp.get("file_path", ""))
                        if k:
                            reads[k] += 1
                            if k == "README(map)" and (inp.get("offset") or inp.get("limit")):
                                readme_partial += 1
                    elif name == "Grep":
                        k = key_for(inp.get("path", "") or "")
                        if k:
                            agg_grep[k] += 1
                    elif name == "Skill":
                        skills[inp.get("skill")] += 1
                    elif name in ("Agent", "Task"):
                        agents[inp.get("subagent_type")] += 1
        if o.get("type") == "user":
            for c in msg.get("content") or [] if isinstance(msg.get("content"), list) else []:
                if isinstance(c, dict) and c.get("type") == "tool_result":
                    name, inp = tool_by_id.get(c.get("tool_use_id"), (None, {}))
                    content = c.get("content")
                    text = content if isinstance(content, str) else json.dumps(content)
                    if name == "Read":
                        k = key_for(inp.get("file_path", ""))
                        if k:
                            chars[k] += len(text)
                        if re.search(r"exceeds maximum|too large|truncated", text[:600], re.I):
                            errors[(key_for(inp.get('file_path','')), text[:140])] += 1
    agg_reads.update(reads); agg_chars.update(chars)
    per_session.append((os.path.basename(f)[:8], "sub" if "subagents" in f else "main",
                        first_inputs, max_ctx, n_assistant,
                        reads.get("README(map)", 0), readme_partial, reads.get("NEXT", 0),
                        sum(chars.values())))

print(f"transcripts: {len(files)}")
print("\nRead calls / result chars by doc class (all sessions):")
for k, n in agg_reads.most_common():
    print(f"  {k:16s} reads={n:4d}  chars={agg_chars[k]:>10,}  ~tok={agg_chars[k]//4:>9,}")
print("\nGrep path targets:", dict(agg_grep))
print("\nSkills:", dict(skills))
print("Agents:", dict(agents))
print("\nRead errors/truncations:")
for (k, t), n in errors.most_common(10):
    print(f"  {n}x {k}: {t!r}")
print("\nper session: id kind first_ctx max_ctx turns readme_reads readme_partial next_reads doc_chars")
for row in sorted(per_session, key=lambda r: -(r[3] or 0))[:45]:
    print("  ", *row)
