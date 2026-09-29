# usage: runbatch.sh name variant "ENV=.. ENV=.." ...
cd /c/Users/charl/worktrees/music-app/sturgeon/api
while [ $# -gt 0 ]; do
  name=$1; var=$2; envs=$3; shift 3
  env $envs PYTHONIOENCODING=utf-8 uv run python -u ../exploration/kit/qlook.py ../exploration/r1-rules/$var.py --out ../exploration/r1-rules/runs/$name.json --quiet > ../exploration/r1-rules/$name.txt 2>&1
  echo "== $name"; tail -15 ../exploration/r1-rules/$name.txt | grep -E "^ +(0|1|3|5|10) \||routing"
done
