./run.sh e_pow12f7rd '{"h":"pow","p":12,"b":0.8,"min_sim":0.7,"rd":0.7,"floor_from":1}' &
./run.sh e_pow12f7bo '{"h":"pow","p":12,"b":0.8,"g":"boost","tau":2,"min_sim":0.7,"floor_from":1}' &
./run.sh e_pow16f7rd '{"h":"pow","p":16,"b":0.8,"min_sim":0.7,"rd":0.7,"floor_from":1}' &
wait
./run.sh e_pow12f7bord '{"h":"pow","p":12,"b":0.8,"g":"boost","tau":2,"min_sim":0.7,"rd":0.7,"floor_from":1}' &
./run.sh e_pow12f7rdL '{"h":"pow","p":12,"b":0.8,"min_sim":0.7,"rd":1.0,"rd_last":1,"floor_from":1}' &
./run.sh e_pow12b1f7rd '{"h":"pow","p":12,"b":1.2,"min_sim":0.7,"rd":0.7,"floor_from":1}' &
wait
