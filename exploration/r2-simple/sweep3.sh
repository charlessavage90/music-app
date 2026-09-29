./run.sh e_pow16f7 '{"h":"pow","p":16,"b":0.8,"min_sim":0.7}' &
./run.sh e_pow12f7 '{"h":"pow","p":12,"b":0.8,"min_sim":0.7}' &
./run.sh e_pow16sqf7 '{"h":"pow","p":16,"b":0.8,"g":"sqrt","kcap":10,"min_sim":0.7}' &
wait
./run.sh e_pow16f7nf '{"h":"pow","p":16,"b":0.8,"min_sim":0.7,"keep_floor":0,"keep_ramp":0}' &
./run.sh e_pow16f6 '{"h":"pow","p":16,"b":0.8,"min_sim":0.6}' &
./run.sh e_pow16f7j '{"h":"pow","p":16,"b":0.8,"min_sim":0.7,"junk_pct":0.05,"junk_pen":1.0}' &
wait
