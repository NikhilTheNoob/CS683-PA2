# Task 1 IP-stride vs SPP data

Baseline: no prefetcher. Values are from the 25M warmup / 25M ROI simulations (L1D prefetcher only, LRU everywhere, gcc-7).
The number in brackets is the IP tracker table size. SPP (64) is the submitted configuration (`prefetcher/spp.l1d_pref`).
Accuracy = useful prefetches / prefetches issued to L2. Coverage = fraction of the baseline's L1D load misses removed.

| Trace | Prefetcher | IPC | Speedup vs no prefetcher | L1D Load MPKI | Accuracy | Coverage |
|---|---|---:|---:|---:|---:|---:|
| Trace1 | No prefetcher | 0.232345 | 0.0000% | 10.67800 | - | - |
| Trace1 | IP-stride (24) | 0.233452 | 0.4764% | 10.11900 | 52.7% | 5.2% |
| Trace1 | SPP (24) | 0.234077 | 0.7454% | 9.68924 | 49.8% | 9.3% |
| Trace1 | IP-stride (64) | 0.233918 | 0.6770% | 9.95256 | 57.7% | 6.8% |
| Trace1 | SPP (64) | 0.234531 | 0.9408% | 9.51272 | 51.7% | 10.9% |
| Trace2 | No prefetcher | 0.251158 | 0.0000% | 13.53790 | - | - |
| Trace2 | IP-stride (24) | 0.251260 | 0.0406% | 13.43780 | 38.2% | 0.7% |
| Trace2 | SPP (24) | 0.252350 | 0.4746% | 13.25850 | 41.1% | 2.1% |
| Trace2 | IP-stride (64) | 0.251956 | 0.3177% | 13.33030 | 46.8% | 1.5% |
| Trace2 | SPP (64) | 0.253997 | 1.1304% | 13.02620 | 46.3% | 3.8% |
| Trace3 | No prefetcher | 0.382065 | 0.0000% | 3.40344 | - | - |
| Trace3 | IP-stride (24) | 0.382862 | 0.2086% | 3.31816 | 16.0% | 2.5% |
| Trace3 | SPP (24) | 0.384601 | 0.6638% | 3.14500 | 30.2% | 7.6% |
| Trace3 | IP-stride (64) | 0.384416 | 0.6153% | 3.19488 | 27.8% | 6.1% |
| Trace3 | SPP (64) | 0.391237 | 2.4006% | 2.70744 | 46.5% | 20.4% |

| Prefetcher | Geomean speedup |
|---|---:|
| IP-stride (24) | 0.2417% |
| SPP (24) | 0.6279% |
| IP-stride (64) | 0.5366% |
| SPP (64) | 1.4886% |
