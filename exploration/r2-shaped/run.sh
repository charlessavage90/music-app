# usage: run.sh name 'json' [--rate]
cd /c/Users/charl/worktrees/music-app/sturgeon/api
name=$1; js=$2; shift 2
R2="$js" PYTHONIOENCODING=utf-8 uv run python -u ../exploration/kit/qlook.py ../exploration/r2-shaped/${VAR:-var}.py --out ../exploration/r2-shaped/runs/$name.json --quiet "$@" > ../exploration/r2-shaped/$name.txt 2>&1
echo "$js" >> ../exploration/r2-shaped/$name.txt
echo "== $name $js"; grep -E "^ +(0|1|2|3|5|10) \||routing" ../exploration/r2-shaped/$name.txt
