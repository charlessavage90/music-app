"""Publishing the SPA in the order that does not strand a returning visitor.

`FRO-1`. The obvious way to publish a built SPA is one `aws s3 sync --delete`,
and it is wrong in a way that is invisible from the machine running it. An object
uploaded that way carries `ETag` and `Last-Modified` and **no `Cache-Control`**,
so a browser falls back to heuristic freshness and keeps `index.html` for a
duration nobody chose. `--delete` then removes the hashed asset that the stale
copy names. The visitor's browser asks for a file that is no longer there, and
there is no error boundary — so the symptom is a **white screen with no text**,
on a site that works perfectly for everyone else, including for whoever deployed
it.

Stage 3 fixed this in `infra/README.md` §6, as three ordered passes a person
types. This module exists because that was the only fix in the stage held by
nothing: a runbook step cannot fail a suite, and the operator who gets the order
wrong is precisely the person who cannot observe the consequence.

**Planning is separated from running** so the invariants are testable without
AWS, without credentials and without a build — the same reason `deploy_stage.py`
is a pure function rather than a branch inside `app.py`. `plan_upload` returns
the commands; `main` runs them. Every rule §6 states in prose is an assertion in
`test_sync_frontend.py`.

**The content-type check is new here and is not in §6's command list.** §6 records
it as a machine-state caveat — `aws s3 sync` guesses `Content-Type` from the file
extension, it was correct on the deploy machine on 2026-07-27, and it must be
re-checked if the deploy ever moves machines. A caveat that depends on the
machine and is checked by remembering to check it is worth very little, and its
failure is the *same blank page* as `FRO-1` from an unrelated cause. So it runs
between the two passes: after the assets are up, before `index.html` makes them
live.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
from collections.abc import Iterable
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]

# Where AWS CLI v2 installs itself on Windows. Consulted only when the CLI is
# not on PATH — see resolve_aws.
_AWS_FALLBACKS = [r"C:\Program Files\Amazon\AWSCLIV2\aws.exe"]

# npm ships as a .cmd shim on Windows, which subprocess will not find under the
# bare name. Resolved per-command rather than by running everything through a
# shell: the CloudFormation --query arguments contain quotes, `?` and `[]`, and
# cmd.exe mangles them.
NPM = "npm.cmd" if os.name == "nt" else "npm"

INDEX = "index.html"

# The pairing matters and neither half works alone. Hashed filenames change
# whenever content changes, so a year is safe and makes repeat visits free;
# that is what makes it affordable for index.html — the one object whose name
# never changes — to be fetched every time.
ASSET_CACHE_CONTROL = "public,max-age=31536000,immutable"
INDEX_CACHE_CONTROL = "no-cache"

# What a browser will actually execute as a module script. Anything else — most
# likely text/plain from a machine with different extension mappings — is a
# refusal at load time and a blank page for the visitor.
_EXECUTABLE_SCRIPT_TYPES = frozenset({"text/javascript", "application/javascript"})


def plan_upload(
    dist: str,
    bucket: str,
    distribution_id: str,
    prune: bool = False,
    aws: str = "aws",
) -> list[list[str]]:
    """Return the publish commands, in the only order that is safe.

    `prune` adds `--delete` to the asset pass. It is off by default because
    deleting the previous build's assets while the previous `index.html` is
    still live is exactly `FRO-1`. It is legitimate later, once nobody is still
    holding that `index.html`, and at the cutover, where the bucket is empty and
    there is no returning visitor to protect.
    """
    assets = [
        aws, "s3", "sync", f"{dist}/", f"s3://{bucket}/",
        # index.html is excluded from this pass whether or not we are pruning:
        # under --delete, including it would delete the LIVE index.html between
        # the two passes, which takes the site down rather than merely
        # stranding someone mid-visit.
        "--exclude", INDEX,
        "--cache-control", ASSET_CACHE_CONTROL,
    ]
    if prune:
        assets.append("--delete")

    index = [
        aws, "s3", "cp", f"{dist}/{INDEX}", f"s3://{bucket}/{INDEX}",
        "--cache-control", INDEX_CACHE_CONTROL,
    ]

    invalidate = [
        aws, "cloudfront", "create-invalidation",
        "--distribution-id", distribution_id,
        "--paths", "/*",
    ]

    return [assets, index, invalidate]


def check_build_output(names: Iterable[str]) -> None:
    """Refuse a `dist/` that is not a complete build.

    Without this, an empty or half-written directory uploads nothing, issues an
    invalidation, and exits 0 — a deploy that reports success and publishes
    nothing.
    """
    present = list(names)
    if INDEX not in present:
        raise SystemExit(
            f"Refusing to publish: no {INDEX} in the build output.\n"
            "Run `npm run build` in frontend/ first. Publishing without it "
            "would upload nothing, invalidate, and report success."
        )
    if not any(name.endswith(".js") for name in present):
        raise SystemExit(
            "Refusing to publish: the build output contains no JavaScript.\n"
            f"{INDEX} names hashed bundles that are not there, which is a "
            "blank page for every visitor."
        )


def resolve_aws(on_path: str | None, existing_fallbacks: list[str]) -> str:
    """Find the AWS CLI, tolerating a shell whose PATH predates its install.

    A recurring trap on this machine and recorded in project memory: the CLI is
    on the *machine* PATH, so `aws --version` works in a new window, while a
    shell opened earlier cannot see it at all. Left unhandled it surfaces as
    FileNotFoundError partway through a publish — after some objects are up —
    which reads like a broken script rather than a stale environment.
    """
    if on_path:
        return on_path
    if existing_fallbacks:
        return existing_fallbacks[0]
    raise SystemExit(
        "Cannot find the AWS CLI.\n"
        "If `aws --version` works in a NEW terminal, this shell's PATH predates "
        "the install — reopen it and re-run.\n"
        "If it does not, install AWS CLI v2 (infra/README.md section 0)."
    )


def pick_probe_asset(names: Iterable[str]) -> str:
    """Choose the object whose served type decides whether the app runs.

    A script, never `index.html`: the index is uploaded by a different command
    with an explicit type, so probing it would exercise the one object the
    machine-state caveat does not apply to and pronounce the deploy safe.
    """
    return next(name for name in names if name.endswith(".js") and name != INDEX)


def check_asset_content_type(key: str, content_type: str | None) -> None:
    """Refuse a script S3 will serve as something a browser will not run.

    See the module docstring: this is §6's machine-state caveat made mechanical.
    """
    served = (content_type or "").split(";")[0].strip().lower()
    if served not in _EXECUTABLE_SCRIPT_TYPES:
        raise SystemExit(
            f"Refusing to publish: {key} would be served as "
            f"{content_type!r}, which a browser will not execute as a module "
            f"script. Expected one of {sorted(_EXECUTABLE_SCRIPT_TYPES)}.\n"
            "This is the extension-to-type mapping on THIS machine, not a "
            "repository property (infra/README.md §6). The symptom is the same "
            "blank page as FRO-1, from a different cause."
        )


def run(command: list[str], cwd: Path | None = None) -> str:
    """Run one command, failing loudly. Returns stdout."""
    print(f"$ {' '.join(command)}", flush=True)
    done = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    if done.returncode != 0:
        raise SystemExit(
            f"Failed ({done.returncode}): {' '.join(command)}\n{done.stderr}"
        )
    return done.stdout


def find_aws() -> str:
    return resolve_aws(
        shutil.which("aws"),
        [c for c in _AWS_FALLBACKS if Path(c).exists()],
    )


def stack_output(aws: str, stack: str, key: str) -> str:
    value = run([
        aws, "cloudformation", "describe-stacks", "--stack-name", stack,
        "--query", f"Stacks[0].Outputs[?OutputKey=='{key}'].OutputValue",
        "--output", "text",
    ]).strip()
    if not value:
        raise SystemExit(f"Stack {stack} has no output named {key}.")
    return value


def built_files(dist: Path) -> list[str]:
    return sorted(
        p.relative_to(dist).as_posix() for p in dist.rglob("*") if p.is_file()
    )


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        # ASCII only: this prints to a Windows console under cp1252, where a
        # section sign arrives as mojibake and reads like a fault in the tool.
        description="Publish the built SPA - infra/README.md section 6. "
                    "The order of the passes is FRO-1 and is not cosmetic.",
    )
    parser.add_argument("--stack-name", default="ArtistpathStack")
    parser.add_argument("--skip-build", action="store_true",
                        help="publish frontend/dist as it stands")
    parser.add_argument(
        "--prune", action="store_true",
        help="also delete assets the new build no longer names. Safe only once "
             "nobody still holds the previous index.html, and at the cutover, "
             "where the bucket is empty. Never on an ordinary redeploy.",
    )
    args = parser.parse_args(argv)

    frontend = REPO_ROOT / "frontend"
    dist = frontend / "dist"

    aws = find_aws()
    bucket = stack_output(aws, args.stack_name, "SpaBucketName")
    distribution_id = stack_output(aws, args.stack_name, "DistributionId")

    if not args.skip_build:
        run([NPM, "run", "build"], cwd=frontend)

    check_build_output(built_files(dist))
    assets, index, invalidate = plan_upload(
        dist=str(dist), bucket=bucket, distribution_id=distribution_id,
        prune=args.prune, aws=aws,
    )

    run(assets)

    # Between the passes, deliberately: the assets are up but nothing names them
    # yet, so this is the last moment a wrong Content-Type can be caught before
    # index.html makes it a blank page for every visitor.
    probe = pick_probe_asset(built_files(dist))
    served = run([
        aws, "s3api", "head-object", "--bucket", bucket, "--key", probe,
        "--query", "ContentType", "--output", "text",
    ]).strip()
    check_asset_content_type(probe, served)
    print(f"  {probe} is served as {served}", flush=True)

    run(index)
    run(invalidate)
    print("\nPublished. index.html is uncached, so the next visit picks it up.")
    if not args.prune:
        print("Assets from previous builds were left in place (FRO-1). "
              "Prune later with --prune.")


if __name__ == "__main__":
    main()
