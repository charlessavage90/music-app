#!/bin/bash
# usage: sweep.sh name 'json' ...   (pairs)
cd C:/Users/charl/worktrees/music-app/sturgeon/api
export PYTHONIOENCODING=utf-8
while [ $# -gt 0 ]; do
  name=$1; js=$2; shift 2
  R1="$js" uv run python -u ../exploration/kit/qlook.py ../exploration/r1-edgecost/var.py --out ../exploration/r1-edgecost/runs/$name.json --quiet > ../exploration/r1-edgecost/$name.txt 2>&1
  echo "$js" >> ../exploration/r1-edgecost/$name.txt
  echo "== $name $js"; grep -E "^ +(0|3|5|10) \|" ../exploration/r1-edgecost/$name.txt
done
