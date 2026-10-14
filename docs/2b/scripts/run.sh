#!/bin/bash
# Run every 2b configuration on every trace in parallel (25M warmup, 25M sim).
# Override the list with e.g. CONFIGS="rrip irrip" ./docs/2b/scripts/run.sh
cd "$(dirname "$0")/../../.."
mkdir -p docs/2b/results
for cfg in ${CONFIGS:-rrip irrip dyn_irrip_t100 dyn_irrip_t200 dyn_irrip_t250 dyn_irrip_t350 dyn_irrip_t500}; do
    bin=bin/hashed_perceptron-no-no-no-no-no-no-no-lru-lru-lru-$cfg-lru-lru-lru-lru-1core-$cfg
    for t in traces/*.champsimtrace.gz; do
        name=$(basename $t .champsimtrace.gz)
        $bin -warmup_instructions 25000000 -simulation_instructions 25000000 -traces $t > docs/2b/results/${name}_$cfg.txt 2>&1 &
    done
done
wait
