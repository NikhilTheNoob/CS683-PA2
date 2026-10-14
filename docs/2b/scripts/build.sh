#!/bin/bash
# Build RRIP, I-RRIP and Dynamic I-RRIP at 5 thresholds (no L1D prefetcher).
# Thresholds are in per-mille; each variant is a temporary copy of
# dyn_irrip.l2c_repl with DYN_THRESHOLD_PERMILLE overridden.
set -e
cd "$(dirname "$0")/../../.."
./build_champsim.sh no rrip rrip
./build_champsim.sh no irrip irrip
for t in 100 200 250 350 500; do
    f=replacement/dyn_irrip_t$t.l2c_repl
    sed "s/^#define DYN_THRESHOLD_PERMILLE .*/#define DYN_THRESHOLD_PERMILLE $t/" replacement/dyn_irrip.l2c_repl > $f
    ./build_champsim.sh no dyn_irrip_t$t dyn_irrip_t$t
    rm -f $f
done
ls bin
