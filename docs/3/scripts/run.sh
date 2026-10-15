#!/bin/bash
# Build and run the Task 3 configurations on Trace1-3 (25M warmup + 25M sim).
# The plain dynamic I-RRIP (before prefetch awareness) is rebuilt from commit 0ae1bb8.
set -e
cd "$(dirname "$0")/../../.."
git show 0ae1bb8:replacement/dyn_irrip.l2c_repl > replacement/dyn_irrip_plain.l2c_repl
./build_champsim.sh no lru no
./build_champsim.sh spp lru spp_lru
./build_champsim.sh spp rrip spp_rrip
./build_champsim.sh no dyn_irrip dyn
./build_champsim.sh spp dyn_irrip_plain spp_dyn_plain
./build_champsim.sh spp dyn_irrip spp_dyn
rm -f replacement/dyn_irrip_plain.l2c_repl
mkdir -p docs/3/results
for cfg in no spp_lru spp_rrip dyn spp_dyn_plain spp_dyn; do
    bin=$(ls bin/*-1core-$cfg)
    for t in traces/Trace?.*gz; do
        name=$(basename $t | cut -d. -f1)
        $bin -warmup_instructions 25000000 -simulation_instructions 25000000 -traces $t > docs/3/results/${name}_$cfg.txt 2>&1 &
    done
done
wait
