#!/bin/bash
# usage: run.sh NAME [--rate] ; env R2_* configure eng.py
name=$1; shift
cd /c/Users/charl/worktrees/music-app/sturgeon/api
PYTHONIOENCODING=utf-8 uv run python -u ../exploration/kit/qlook.py ../exploration/r2-nsim/eng.py --out ../exploration/r2-nsim/runs/$name.json "$@" > ../exploration/r2-nsim/$name.txt 2>&1
tail -15 ../exploration/r2-nsim/$name.txt
