#!/bin/bash
# usage: sweep.sh name 'json' [name 'json' ...]   (runs sequentially, prints summary rows 0,3,5,10 + continuity)
cd "$(dirname "$0")/../../api"
while [ $# -gt 0 ]; do
  n=$1; j=$2; shift 2
  R2="$j" PYTHONIOENCODING=utf-8 uv run python -u ../exploration/kit/qlook.py ../exploration/r2-tiers/${V:-tiers.py} --out ../exploration/r2-tiers/runs/$n.json --quiet $RATE > ../exploration/r2-tiers/$n.txt 2>&1
  echo "R2=$j" >> ../exploration/r2-tiers/$n.txt
  echo "== $n $j"; grep -E "^ +(0|3|5|10) \|" ../exploration/r2-tiers/$n.txt; grep "routing time" ../exploration/r2-tiers/$n.txt
  (cd ../exploration/r2-tiers && python continuity.py runs/$n.json)
done
