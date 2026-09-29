#!/bin/bash
cd /c/Users/charl/worktrees/music-app/sturgeon/exploration/r2-nsim
export RATER_WORKERS=2
./runv.sh dig_overlap.py A2_R --rate --procs 3
./runv.sh dig_overlap_gentle.py G2_R --rate --procs 3
echo ALLDONE
