#!/usr/bin/env python3
"""Positive control for scripts/issues.py: every check must be shown to go RED as well as green.
A check that cannot fail is the vacuous-check pattern this project has recorded four times.

    python scripts/issues-selftest.py
"""
import importlib.util
import pathlib
import sys

spec = importlib.util.spec_from_file_location("issues", pathlib.Path(__file__).with_name("issues.py"))
issues = importlib.util.module_from_spec(spec)
spec.loader.exec_module(issues)

FAILED = 0


def check(name, cond):
    global FAILED
    print(("  PASS  " if cond else "  FAIL  ") + name)
    FAILED += not cond


def issue(num, labels=(), body="", blocked=0, subs=(0, 0)):
    return {"number": num, "title": f"t{num}", "labels": [{"name": x} for x in labels], "body": body,
            "issue_dependencies_summary": {"blocked_by": blocked, "total_blocked_by": blocked},
            "sub_issues_summary": {"total": subs[0], "completed": subs[1]}}


# Issue-form output shape (### heading, then the value) ...
FORM = """### What happens

x

### Source

docs/a.md

### Done when

y

### Reads contracts

graph-identity, quantities

### Changes contracts

None
"""
# ... and the hand-written shape used by migrated issues (**Heading:** value).
HAND = """**What:** x

**Source:** docs/a.md

**Done when:** y

**Reads contracts:** `cost-function`

**Changes contracts:** quantities
"""

print("parse")
check("form: reads parsed", issues.parse_contracts(FORM, "Reads contracts") == ({"graph-identity", "quantities"}, set()))
check("form: 'None' is an empty declaration, not an absent one", issues.parse_contracts(FORM, "Changes contracts") == (set(), set()))
check("hand: backticked token parsed", issues.parse_contracts(HAND, "Reads contracts") == ({"cost-function"}, set()))
check("absent section is None", issues.parse_contracts("**Source:** x", "Reads contracts") == (None, set()))
check("unknown token is reported, not dropped",
      issues.parse_contracts("**Reads contracts:** popularity", "Reads contracts") == (set(), {"popularity"}))
check("_No response_ counts as absent", issues.parse_contracts("### Reads contracts\n\n_No response_\n", "Reads contracts")[0] is None)

print("ready")
check("clean form issue passes", issues.ready_problems(issue(1, ["task", "agent-ready"], FORM)) == [])
check("clean hand issue passes", issues.ready_problems(issue(1, ["bug", "agent-ready"], HAND)) == [])
for lb in ("owner-hands", "owner-decision", "claimed", "deferred"):
    check(f"goes red on {lb}", any(lb in p for p in issues.ready_problems(issue(1, ["agent-ready", lb], FORM))))
check("goes red when blocked", any("blocked" in p for p in issues.ready_problems(issue(1, [], FORM, blocked=1))))
check("goes red with open sub-issues", any("sub-issues" in p for p in issues.ready_problems(issue(1, [], FORM, subs=(2, 1)))))
check("green when all sub-issues done", issues.ready_problems(issue(1, [], FORM, subs=(2, 2))) == [])
check("goes red with no contracts", any("Reads contracts" in p for p in issues.ready_problems(issue(1, [], "**Source:** a\n**Done when:** b"))))
check("goes red with no Done when", any("Done when" in p for p in issues.ready_problems(issue(1, [], FORM.replace("Done when", "Later")))))
check("goes red on an unknown contract", any("unknown" in p for p in issues.ready_problems(issue(1, [], HAND.replace("quantities", "fame")))))

print("conflicts")
r = lambda n, reads, changes: issue(n, body=f"**Reads contracts:** {reads}\n**Changes contracts:** {changes}")
check("reader x reader: no conflict", issues.conflicts([r(1, "quantities", "none"), r(2, "quantities", "none")]) == [])
check("writer x reader: conflict (the popularity-semantics case)",
      issues.conflicts([r(1, "none", "quantities"), r(2, "quantities", "none")]) == [(1, 2, {"quantities"})])
check("reader x writer, reversed order: conflict",
      issues.conflicts([r(1, "quantities", "none"), r(2, "none", "quantities")]) == [(1, 2, {"quantities"})])
check("writer x writer: conflict", issues.conflicts([r(1, "none", "api-wire"), r(2, "none", "api-wire")]) == [(1, 2, {"api-wire"})])
check("disjoint writers: no conflict", issues.conflicts([r(1, "none", "api-wire"), r(2, "none", "url-state")]) == [])

print("vocabulary")
tmpl = pathlib.Path(__file__).parents[1] / ".github" / "ISSUE_TEMPLATE"
for f in sorted(tmpl.glob("[0-9]-*.yml")):
    text = f.read_text(encoding="utf-8")
    check(f"{f.name} offers every contract", all(f'"{c}"' in text for c in issues.CONTRACTS))
    import re as _re
    offered = set(_re.findall(r'^        - "([a-z0-9-]+)"$', text, _re.M)) - {"none"}
    check(f"{f.name} offers nothing outside the vocabulary", offered == set(issues.CONTRACTS))
doc = (pathlib.Path(__file__).parents[1] / "docs" / "superpowers" / "ISSUES.md").read_text(encoding="utf-8")
check("ISSUES.md defines every contract", all(f"| `{c}` |" in doc for c in issues.CONTRACTS))

print(f"\n{'FAILED' if FAILED else 'all passed'}")
sys.exit(1 if FAILED else 0)
