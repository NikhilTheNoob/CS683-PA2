# Task 3: SPP + prefetch-aware dynamic I-RRIP

25M warmup + 25M simulated instructions, GCC 7.5 (Ubuntu 20.04 package). Speedup is IPC over no prefetcher + LRU.
Accuracy and coverage are for the L1D prefetcher; coverage is the fraction of the no-prefetcher L1D load misses removed.
Regenerate with `docs/3/scripts/run.sh` and then `python3 docs/3/scripts/plot.py`; raw output is in `results/`.

| Trace | Configuration | IPC | Speedup | L1D acc. | L1D cov. | L1D load MPKI | L2C load MPKI | L2 instr. load MPKI | L2 data load MPKI |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Trace1 | No prefetcher + LRU | 0.232345 | 1.0000 | - | - | 10.678 | 17.696 | 10.338 | 7.358 |
| Trace1 | SPP + LRU | 0.234546 | 1.0095 | 51.3% | 10.8% | 9.528 | 16.751 | 10.404 | 6.347 |
| Trace1 | SPP + RRIP | 0.234362 | 1.0087 | 51.7% | 10.9% | 9.519 | 16.747 | 10.645 | 6.102 |
| Trace1 | Dyn I-RRIP (no prefetcher) | 0.232289 | 0.9998 | - | - | 10.679 | 17.539 | 10.042 | 7.497 |
| Trace1 | SPP + Dyn I-RRIP (not prefetch-aware) | 0.234381 | 1.0088 | 51.9% | 10.7% | 9.531 | 16.596 | 10.107 | 6.489 |
| Trace1 | SPP + prefetch-aware Dyn I-RRIP | 0.234555 | 1.0095 | 51.4% | 10.8% | 9.525 | 16.487 | 10.040 | 6.447 |
| Trace2 | No prefetcher + LRU | 0.251158 | 1.0000 | - | - | 13.538 | 27.357 | 18.853 | 8.504 |
| Trace2 | SPP + LRU | 0.254259 | 1.0123 | 51.1% | 3.8% | 13.018 | 26.898 | 18.894 | 8.004 |
| Trace2 | SPP + RRIP | 0.254800 | 1.0145 | 51.2% | 3.7% | 13.031 | 25.271 | 17.809 | 7.462 |
| Trace2 | Dyn I-RRIP (no prefetcher) | 0.255532 | 1.0174 | - | - | 13.540 | 23.219 | 14.387 | 8.833 |
| Trace2 | SPP + Dyn I-RRIP (not prefetch-aware) | 0.258805 | 1.0304 | 51.1% | 3.8% | 13.022 | 22.706 | 14.391 | 8.315 |
| Trace2 | SPP + prefetch-aware Dyn I-RRIP | 0.258921 | 1.0309 | 51.4% | 3.8% | 13.021 | 22.550 | 14.240 | 8.310 |
| Trace3 | No prefetcher + LRU | 0.382065 | 1.0000 | - | - | 3.403 | 3.954 | 1.124 | 2.830 |
| Trace3 | SPP + LRU | 0.391621 | 1.0250 | 48.0% | 21.5% | 2.672 | 3.089 | 1.142 | 1.947 |
| Trace3 | SPP + RRIP | 0.391432 | 1.0245 | 48.3% | 21.2% | 2.682 | 3.174 | 1.204 | 1.970 |
| Trace3 | Dyn I-RRIP (no prefetcher) | 0.381908 | 0.9996 | - | - | 3.403 | 3.957 | 1.082 | 2.875 |
| Trace3 | SPP + Dyn I-RRIP (not prefetch-aware) | 0.391587 | 1.0249 | 47.6% | 21.5% | 2.671 | 3.090 | 1.099 | 1.991 |
| Trace3 | SPP + prefetch-aware Dyn I-RRIP | 0.391726 | 1.0253 | 48.0% | 21.6% | 2.667 | 3.048 | 1.070 | 1.978 |

## Speedup of SPP + prefetch-aware Dyn I-RRIP over each reference

| Reference | Trace1 | Trace2 | Trace3 | Geomean |
|---|---:|---:|---:|---:|
| SPP + LRU | 1.0000 | 1.0183 | 1.0003 | 1.0062 |
| SPP + RRIP | 1.0008 | 1.0162 | 1.0008 | 1.0059 |
| Dyn I-RRIP (no prefetcher) | 1.0098 | 1.0133 | 1.0257 | 1.0162 |
| SPP + Dyn I-RRIP (not prefetch-aware) | 1.0007 | 1.0004 | 1.0004 | 1.0005 |

| Configuration | Geomean speedup over no prefetcher |
|---|---:|
| No prefetcher + LRU | 1.0000 |
| SPP + LRU | 1.0156 |
| SPP + RRIP | 1.0159 |
| Dyn I-RRIP (no prefetcher) | 1.0056 |
| SPP + Dyn I-RRIP (not prefetch-aware) | 1.0213 |
| SPP + prefetch-aware Dyn I-RRIP | 1.0219 |
