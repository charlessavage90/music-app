#!/bin/bash
# usage: run.sh NAME 'JSON' [--rate]
cd /c/Users/charl/worktrees/music-app/sturgeon/api
name=$1; shift; js=$1; shift
R2="$js" PYTHONIOENCODING=utf-8 uv run python -u ../exploration/kit/qlook.py ../exploration/r2-simple/var.py --out ../exploration/r2-simple/runs/$name.json --quiet "$@" > ../exploration/r2-simple/$name.txt 2>&1
echo "PARAMS $js" >> ../exploration/r2-simple/$name.txt
