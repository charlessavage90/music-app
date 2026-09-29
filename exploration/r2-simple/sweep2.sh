./run.sh pow16f7 '{"h":"pow","p":16,"b":0.8,"min_sim":0.7}' &
./run.sh pow8b1f7 '{"h":"pow","p":8,"b":1.0,"min_sim":0.7}' &
wait
./run.sh pow8satf7 '{"h":"pow","p":8,"b":0.6,"g":"sat","tau":3,"min_sim":0.7}' &
./run.sh logx8f7 '{"h":"logx","thr":0.8,"b":0.3,"min_sim":0.7}' &
wait
./run.sh pow8f7nf '{"h":"pow","p":8,"b":0.6,"min_sim":0.7,"keep_floor":0,"keep_ramp":0}' &
./run.sh pow8f75 '{"h":"pow","p":8,"b":0.6,"min_sim":0.75}' &
wait
