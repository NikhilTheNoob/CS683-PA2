#!/bin/bash
# Build no-prefetcher, IP-stride and SPP (LRU L2) and run Trace1-3, 25M warmup + 25M sim.
# Raw ChampSim output goes to docs/1/results/<Trace>_<config>.txt.
set -e
cd "$(dirname "$0")/../../.."
./build_champsim.sh no lru no
./build_champsim.sh ip_stride lru ipstride
./build_champsim.sh spp lru spp
mkdir -p docs/1/results
for cfg in no ipstride spp; do
    bin=$(ls bin/*-1core-$cfg)
    for t in traces/Trace?.*gz; do
        name=$(basename $t | cut -d. -f1)
        $bin -warmup_instructions 25000000 -simulation_instructions 25000000 -traces $t > docs/1/results/${name}_$cfg.txt 2>&1 &
    done
done
wait
