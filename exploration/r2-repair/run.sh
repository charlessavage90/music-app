#!/bin/bash
# usage: run.sh NAME VARIANT_FILE 'JSON' [--rate]
cd /c/Users/charl/worktrees/music-app/sturgeon/api
name=$1; var=$2; js=$3; shift 3
rm -f ../exploration/r2-repair/runs/log_$name.txt
R2="$js" R2LOG=log_$name.txt RATER_WORKERS=2 PYTHONIOENCODING=utf-8 uv run python -u ../exploration/kit/qlook.py ../exploration/r2-repair/$var --out ../exploration/r2-repair/runs/$name.json "$@" > ../exploration/r2-repair/$name.txt 2>../exploration/r2-repair/runs/$name.err
echo "R2=$js" >> ../exploration/r2-repair/$name.txt
tail -15 ../exploration/r2-repair/$name.txt
L=../exploration/r2-repair/runs/log_$name.txt
[ -f $L ] && cut -f2 $L | sed 's/ w=.*//' | sort | uniq -c
