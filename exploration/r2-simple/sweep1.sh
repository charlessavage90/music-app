./run.sh ftB '{"h":"knee","thr":0.9,"b":0.3}' &
./run.sh log15 '{"h":"log","b":0.15}' &
wait
./run.sh log15f7 '{"h":"log","b":0.15,"min_sim":0.7}' &
./run.sh log10f7 '{"h":"log","b":0.10,"min_sim":0.7}' &
wait
./run.sh pow8f7 '{"h":"pow","p":8,"b":0.6,"min_sim":0.7}' &
./run.sh ftBf7 '{"h":"knee","thr":0.9,"b":0.3,"min_sim":0.7}' &
wait
