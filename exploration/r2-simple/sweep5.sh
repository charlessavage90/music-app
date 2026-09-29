./run.sh e_pow12bo_rdg10 '{"h":"pow","p":12,"b":0.8,"g":"boost","tau":2,"min_sim":0.7,"rd":0.7,"rd_gap":0.1,"floor_from":1}' &
./run.sh e_pow12bo_rdg15 '{"h":"pow","p":12,"b":0.8,"g":"boost","tau":2,"min_sim":0.7,"rd":0.7,"rd_gap":0.15,"floor_from":1}' &
./run.sh e_pow12_rdg10 '{"h":"pow","p":12,"b":0.8,"min_sim":0.7,"rd":0.7,"rd_gap":0.1,"floor_from":1}' &
wait
