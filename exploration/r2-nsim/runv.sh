#!/bin/bash
# usage: runv.sh VARIANT_FILE NAME [qlook args]
v=$1; name=$2; shift 2
cd /c/Users/charl/worktrees/music-app/sturgeon/api
PYTHONIOENCODING=utf-8 uv run python -u ../exploration/kit/qlook.py ../exploration/r2-nsim/$v --out ../exploration/r2-nsim/runs/$name.json "$@" > ../exploration/r2-nsim/$name.txt 2>&1
