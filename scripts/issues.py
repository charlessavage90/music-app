#!/usr/bin/env python3
"""Mechanical checks over this repo's GitHub issues — the half of docs/superpowers/ISSUES.md that a
script can enforce, so the judgement half is all that is left to whoever applies a label.

    python scripts/issues.py lint [N ...]       # the agent-ready checklist's mechanical items (§4)
    python scripts/issues.py conflicts [N ...]  # contract collisions among live issues (§5)
    python scripts/issues.py readers CONTRACT   # open issues that read or change CONTRACT (merge time)
    python scripts/issues.py stale [--days D]   # claims with no open PR and no recent activity
    python scripts/issues.py unblocked          # issues whose native blockers have all closed

Exit status is 1 when `lint` or `conflicts` finds anything, so a ritual can gate on it.
Reads only; never edits an issue. Positive control: scripts/issues-selftest.py.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys

# The contract vocabulary. ISSUES.md §5 owns what each one means and where its current value lives;
# this tuple must match that table and the dropdown options in .github/ISSUE_TEMPLATE/.
CONTRACTS = (
    "graph-identity",
    "apg1-format",
    "quantities",
    "cost-function",
    "requirements",
    "api-wire",
    "url-state",
    "edge-behaviour",
    "deploy-path",
    "rituals",
)
READS_HEADING = "Reads contracts"
CHANGES_HEADING = "Changes contracts"
OWNER_LABELS = {"owner-decision", "owner-hands"}
LIVE_LABELS = {"agent-ready", "claimed"}


# ---- pure functions (tested by issues-selftest.py) -------------------------------------------

def _section(body: str, heading: str) -> str | None:
    """Text under a `### heading` (issue-form output) or a `**heading:**` line, else None."""
    m = re.search(rf"^#+\s*{re.escape(heading)}\s*$\n(.*?)(?=^#+\s|\Z)", body, re.M | re.S | re.I)
    if m:
        return m.group(1).strip()
    m = re.search(rf"^\*\*{re.escape(heading)}:?\*\*:?\s*(.*)$", body, re.M | re.I)
    return m.group(1).strip() if m else None


def parse_contracts(body: str, heading: str) -> tuple[set[str] | None, set[str]]:
    """(declared contracts or None if the section is absent/empty, unknown tokens)."""
    text = _section(body or "", heading)
    if text is None or text in ("", "_No response_"):
        return None, set()
    tokens = {t.strip().strip("`").lower() for t in re.split(r"[,\n]", text) if t.strip()}
    tokens.discard("none")
    unknown = {t for t in tokens if t not in CONTRACTS}
    return tokens - unknown, unknown


def has_section(body: str, heading: str) -> bool:
    text = _section(body or "", heading)
    return bool(text) and text != "_No response_"


def ready_problems(issue: dict) -> list[str]:
    """Mechanical failures of the agent-ready checklist (ISSUES.md §4). Empty list = passes."""
    labels = {lb["name"] for lb in issue.get("labels", [])}
    body = issue.get("body") or ""
    out = []
    for lb in sorted(labels & OWNER_LABELS):
        out.append(f"carries {lb}: an owner's issue is never agent-ready — split off the session's part")
    if "claimed" in labels:
        out.append("carries claimed: a claim removes agent-ready (§6)")
    if "deferred" in labels:
        out.append("still labelled deferred: when the condition comes due, the kind becomes task/bug")
    deps = issue.get("issue_dependencies_summary") or {}
    if deps.get("blocked_by", 0):
        out.append(f"blocked by {deps['blocked_by']} open issue(s)")
    subs = issue.get("sub_issues_summary") or {}
    if subs.get("total", 0) - subs.get("completed", 0) > 0:
        out.append("has open sub-issues: dispatch those, not the parent")
    for heading in ("Source", "Done when"):
        if not has_section(body, heading):
            out.append(f"no '{heading}' section")
    for heading in (READS_HEADING, CHANGES_HEADING):
        declared, unknown = parse_contracts(body, heading)
        if declared is None and not unknown:
            out.append(f"no '{heading}' section (write 'none' if it touches none)")
        if unknown:
            out.append(f"'{heading}' names unknown contract(s): {', '.join(sorted(unknown))}")
    return out


def contracts_of(issue: dict) -> tuple[set[str], set[str]]:
    body = issue.get("body") or ""
    reads = parse_contracts(body, READS_HEADING)[0] or set()
    changes = parse_contracts(body, CHANGES_HEADING)[0] or set()
    return reads, changes


def conflicts(issues: list[dict]) -> list[tuple[int, int, set[str]]]:
    """Pairs that must not run concurrently: one changes a contract the other reads or changes."""
    rc = {i["number"]: contracts_of(i) for i in issues}
    out = []
    nums = sorted(rc)
    for x_i, a in enumerate(nums):
        for b in nums[x_i + 1:]:
            ra, ca = rc[a]
            rb, cb = rc[b]
            shared = (ca & (rb | cb)) | (cb & ra)
            if shared:
                out.append((a, b, shared))
    return out


# ---- GitHub access -----------------------------------------------------------------------------

def _gh_json(args: list[str]):
    res = subprocess.run(["gh", *args], capture_output=True, text=True, encoding="utf-8")
    if res.returncode:
        sys.exit(f"gh {' '.join(args)} failed:\n{res.stderr}")
    return json.loads(res.stdout or "null")


def open_issues() -> list[dict]:
    # The REST listing carries the native dependency and sub-issue summaries; `gh issue list` does not.
    pages = _gh_json(["api", "--paginate", "--slurp", "repos/{owner}/{repo}/issues?state=open&per_page=100"])
    return [i for page in pages for i in page if "pull_request" not in i]


def _labels(issue: dict) -> set[str]:
    return {lb["name"] for lb in issue.get("labels", [])}


def _title(issue: dict) -> str:
    return f"#{issue['number']} {issue['title']}"


# ---- commands ----------------------------------------------------------------------------------

def cmd_lint(nums: list[int]) -> int:
    issues = open_issues()
    targets = [i for i in issues if i["number"] in nums] if nums else [
        i for i in issues if "agent-ready" in _labels(i)]
    bad = 0
    for i in targets:
        probs = ready_problems(i)
        print(("FAIL  " if probs else "ok    ") + _title(i))
        for p in probs:
            print(f"        - {p}")
        bad += bool(probs)
    print(f"\n{len(targets) - bad} pass, {bad} fail (mechanical items only — §4's judgement items are not checked)")
    return 1 if bad else 0


def cmd_conflicts(nums: list[int]) -> int:
    issues = open_issues()
    live = [i for i in issues if _labels(i) & LIVE_LABELS]
    if nums:
        live += [i for i in issues if i["number"] in nums and i not in live]
    found = conflicts(live)
    if nums:
        found = [c for c in found if c[0] in nums or c[1] in nums]
    by_num = {i["number"]: i for i in live}
    for a, b, shared in found:
        state = lambda n: "claimed" if "claimed" in _labels(by_num[n]) else "ready"
        print(f"#{a} ({state(a)}) x #{b} ({state(b)}): {', '.join(sorted(shared))}")
    undeclared = [i for i in live if not any(contracts_of(i))
                  and parse_contracts(i.get("body") or "", READS_HEADING)[0] is None]
    for i in undeclared:
        print(f"undeclared (cannot be checked): {_title(i)}")
    print(f"\n{len(found)} conflicting pair(s) among {len(live)} live issue(s)")
    return 1 if found else 0


def cmd_readers(contract: str) -> int:
    if contract not in CONTRACTS:
        sys.exit(f"unknown contract {contract!r}; known: {', '.join(CONTRACTS)}")
    for i in open_issues():
        reads, changes = contracts_of(i)
        if contract in reads | changes:
            how = "changes" if contract in changes else "reads"
            print(f"{how:8}{_title(i)}")
    return 0


def cmd_stale(days: int) -> int:
    prs = _gh_json(["pr", "list", "--state", "open", "--limit", "200", "--json", "number,body,title"])
    now = dt.datetime.now(dt.timezone.utc)
    for i in open_issues():
        if "claimed" not in _labels(i):
            continue
        n = i["number"]
        linked = [p["number"] for p in prs
                  if re.search(rf"#{n}\b", (p.get("body") or "") + " " + p["title"])]
        age = (now - dt.datetime.fromisoformat(i["updated_at"].replace("Z", "+00:00"))).days
        if not linked and age >= days:
            print(f"stale claim ({age}d, no open PR): {_title(i)}")
        elif not linked:
            print(f"claimed, no PR yet ({age}d):      {_title(i)}")
    return 0


def cmd_unblocked() -> int:
    for i in open_issues():
        deps = i.get("issue_dependencies_summary") or {}
        labels = _labels(i)
        if deps.get("total_blocked_by", 0) and not deps.get("blocked_by", 0) and not labels & LIVE_LABELS:
            owner = ", ".join(sorted(labels & OWNER_LABELS))
            print(f"unblocked{' (' + owner + ')' if owner else ''}: {_title(i)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("lint", "conflicts"):
        sub.add_parser(name).add_argument("nums", nargs="*", type=int)
    sub.add_parser("readers").add_argument("contract")
    sub.add_parser("stale").add_argument("--days", type=int, default=3)
    sub.add_parser("unblocked")
    a = ap.parse_args(argv)
    if a.cmd == "lint":
        return cmd_lint(a.nums)
    if a.cmd == "conflicts":
        return cmd_conflicts(a.nums)
    if a.cmd == "readers":
        return cmd_readers(a.contract)
    if a.cmd == "stale":
        return cmd_stale(a.days)
    return cmd_unblocked()


if __name__ == "__main__":
    sys.exit(main())
